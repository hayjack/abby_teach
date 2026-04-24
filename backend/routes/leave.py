from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import LeaveRecord, Student, Course
from extensions import db
from datetime import date
from utils import parse_date
from leave_sync import sync_attendance_with_leave, cancel_leave_sync
import logging

logger = logging.getLogger(__name__)

leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/', methods=['GET'])
@jwt_required()
def get_leave_records():
    student_id = request.args.get('student_id')
    course_id = request.args.get('course_id')
    status = request.args.get('status')
    query = LeaveRecord.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if status:
        query = query.filter_by(status=status)
    records = query.all()
    return jsonify([{
        'id': record.id,
        'student_id': record.student_id,
        'student_name': record.student.name,
        'course_id': record.course_id,
        'course_name': record.course.name,
        'start_date': record.start_date.isoformat(),
        'end_date': record.end_date.isoformat(),
        'reason': record.reason,
        'status': record.status
    } for record in records])

@leave_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_leave_record(id):
    record = LeaveRecord.query.get(id)
    if not record:
        return jsonify({'message': '请假记录不存在'}), 404
    return jsonify({
        'id': record.id,
        'student_id': record.student_id,
        'student_name': record.student.name,
        'course_id': record.course_id,
        'course_name': record.course.name,
        'start_date': record.start_date.isoformat(),
        'end_date': record.end_date.isoformat(),
        'reason': record.reason,
        'status': record.status
    })

@leave_bp.route('/', methods=['POST'])
@jwt_required()
def create_leave_record():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason')
    
    if not student_id or not course_id or not start_date or not end_date:
        return jsonify({'message': '学生、课程、开始日期和结束日期均为必填项'}), 400
    
    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    
    if not parsed_start or not parsed_end:
        return jsonify({'message': '日期格式不正确，请使用 YYYY-MM-DD 格式'}), 400
    
    if parsed_end < parsed_start:
        return jsonify({'message': '结束日期不能小于开始日期'}), 400
    
    logger.info(f'[请假] 创建请假记录: student_id={student_id}, course_id={course_id}, date={start_date}~{end_date}')
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    new_record = LeaveRecord(
        student_id=student_id,
        course_id=course_id,
        start_date=parsed_start,
        end_date=parsed_end,
        reason=reason,
        status='待审批'
    )
    db.session.add(new_record)
    db.session.commit()
    logger.info(f'[请假] 请假记录创建成功: leave_id={new_record.id}')
    return jsonify({'message': '请假记录创建成功', 'id': new_record.id}), 201

@leave_bp.route('/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_leave_record(id):
    record = LeaveRecord.query.get(id)
    if not record:
        return jsonify({'message': '请假记录不存在'}), 404
    
    logger.info(f'[请假] 审批请假记录: leave_id={id}, 学生={record.student.name}, 状态={record.status}')
    
    if record.status == '已批准':
        logger.info(f'[请假] 请假记录已批准，跳过')
        return jsonify({'message': '请假记录已批准'})
    
    record.status = '已批准'
    
    logger.info(f'[请假] 开始执行请假联动...')
    sync_result = sync_attendance_with_leave(record)
    logger.info(f'[请假] 联动结果: {sync_result}')
    
    db.session.commit()
    
    result_message = '请假记录已批准'
    if sync_result['updated_count'] > 0:
        result_message += f'，已联动更新{sync_result["updated_count"]}条考勤记录，恢复{sync_result["hours_restored"]}课时'
    
    logger.info(f'[请假] 审批完成: {result_message}')
    
    return jsonify({
        'message': result_message,
        'sync_result': sync_result
    })

@leave_bp.route('/<int:id>/reject', methods=['PUT'])
@jwt_required()
def reject_leave_record(id):
    record = LeaveRecord.query.get(id)
    if not record:
        return jsonify({'message': '请假记录不存在'}), 404
    record.status = '已拒绝'
    db.session.commit()
    return jsonify({'message': '请假记录已拒绝'})

@leave_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_leave_record(id):
    record = LeaveRecord.query.get(id)
    if not record:
        return jsonify({'message': '请假记录不存在'}), 404
    
    logger.info(f'[请假] 删除请假记录: leave_id={id}, 学生={record.student.name}, 状态={record.status}')
    
    # 如果是已批准的请假记录，需要联动恢复考勤和课时
    cancel_result = None
    if record.status == '已批准':
        logger.info(f'[请假] 删除已批准的请假记录，开始执行撤销联动...')
        cancel_result = cancel_leave_sync(record)
        logger.info(f'[请假] 撤销联动结果: {cancel_result}')
    
    db.session.delete(record)
    db.session.commit()
    
    if cancel_result:
        result_message = f'请假记录已删除，已联动恢复{cancel_result["updated_count"]}条考勤记录，扣除{cancel_result["hours_deducted"]}课时'
        logger.info(f'[请假] 删除完成: {result_message}')
        return jsonify({'message': result_message, 'cancel_result': cancel_result})
    else:
        logger.info(f'[请假] 删除完成（无需联动）')
        return jsonify({'message': '请假记录删除成功'})
