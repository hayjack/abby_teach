from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import LeaveRecord, Student, Course
from extensions import db
from datetime import date
from utils import parse_date
from leave_sync import sync_attendance_with_leave

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
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    new_record = LeaveRecord(
        student_id=student_id,
        course_id=course_id,
        start_date=parse_date(start_date),
        end_date=parse_date(end_date),
        reason=reason,
        status='待审批'
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'message': '请假记录创建成功', 'id': new_record.id}), 201

@leave_bp.route('/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_leave_record(id):
    record = LeaveRecord.query.get(id)
    if not record:
        return jsonify({'message': '请假记录不存在'}), 404
    
    if record.status == '已批准':
        return jsonify({'message': '请假记录已批准'})
    
    record.status = '已批准'
    sync_result = sync_attendance_with_leave(record)
    db.session.commit()
    
    result_message = '请假记录已批准'
    if sync_result['updated_count'] > 0:
        result_message += f'，已联动更新{sync_result["updated_count"]}条考勤记录，恢复{sync_result["hours_restored"]}课时'
    
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
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '请假记录删除成功'})
