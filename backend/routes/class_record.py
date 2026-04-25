from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import ClassRecord, AttendanceRecord, Student, Class, Course, User, StudentCourse, LeaveRecord
from extensions import db
from datetime import date, time, datetime
from utils import parse_date
from permissions import can_manage_any_teacher, can_manage_class
from leave_sync import sync_leave_on_record_creation
import logging

logger = logging.getLogger(__name__)

def parse_time(time_str):
    """Parse time from frontend (handles both 'HH:MM:SS' and full datetime strings like '2026-04-24T07:00:27.000Z')"""
    if not time_str:
        return None
    # If it's a full datetime, extract just the time part
    if 'T' in str(time_str):
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.time()
    return time.fromisoformat(time_str)

class_record_bp = Blueprint('class_record', __name__)

@class_record_bp.route('/', methods=['GET'])
@jwt_required()
def get_class_records():
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 日期范围校验
    if start_date and end_date:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        if parsed_start and parsed_end and parsed_end < parsed_start:
            return jsonify({'message': '结束日期不能小于开始日期'}), 400
    
    query = ClassRecord.query
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    # 按时间倒序排序，最新的记录显示在前面
    query = query.order_by(ClassRecord.class_date.desc(), ClassRecord.start_time.desc())
    
    # 分页查询
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 构建响应数据
    records = []
    for record in pagination.items:
        # 处理补课记录的班级名称
        class_name = '补课'
        if record.class_id != 0 and record.class_:
            class_name = record.class_.name
        
        # 处理课程名称
        course_name = '未知课程'
        if record.course:
            course_name = record.course.name
        
        # 处理教师名称
        teacher_name = '未知教师'
        if record.teacher:
            teacher_name = record.teacher.name
        
        records.append({
            'id': record.id,
            'class_id': record.class_id,
            'class_name': class_name,
            'course_id': record.course_id,
            'course_name': course_name,
            'teacher_id': record.teacher_id,
            'teacher_name': teacher_name,
            'class_date': record.class_date.isoformat(),
            'start_time': record.start_time.isoformat(),
            'end_time': record.end_time.isoformat(),
            'hours': float(record.hours),
            'content': record.content,
            'is_makeup': record.is_makeup
        })
    
    return jsonify({
        'items': records,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@class_record_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_class_record(id):
    record = ClassRecord.query.get(id)
    if not record:
        return jsonify({'message': '上课记录不存在'}), 404
    
    # 获取考勤记录
    attendances = []
    for attendance in record.attendance_records:
        attendances.append({
            'student_id': attendance.student_id,
            'student_name': attendance.student.name,
            'status': attendance.status
        })
    
    # 处理补课记录的班级名称
    class_name = '补课'
    if record.class_id != 0 and record.class_:
        class_name = record.class_.name
    
    return jsonify({
        'id': record.id,
        'class_id': record.class_id,
        'class_name': class_name,
        'course_id': record.course_id,
        'course_name': record.course.name,
        'teacher_id': record.teacher_id,
        'teacher_name': record.teacher.name,
        'class_date': record.class_date.isoformat(),
        'start_time': record.start_time.isoformat(),
        'end_time': record.end_time.isoformat(),
        'hours': float(record.hours),
        'content': record.content,
        'is_makeup': record.is_makeup,
        'attendances': attendances
    })

@class_record_bp.route('/', methods=['POST'])
@jwt_required()
def create_class_record():
    data = request.get_json()
    class_id = data.get('class_id')
    course_id = data.get('course_id')
    class_date = data.get('class_date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    hours = data.get('hours')
    content = data.get('content')
    
    logger.info(f'[上课记录] 创建请求: class_id={class_id}, course_id={course_id}, date={class_date}, hours={hours}')
    
    # 检查班级是否存在
    class_ = Class.query.get(class_id)
    if not class_:
        logger.error(f'[上课记录] 班级ID={class_id} 不存在')
        return jsonify({'message': '班级不存在'}), 404
    
    # 权限检查：获取当前用户
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在'}), 404
    
    logger.info(f'[上课记录] 当前用户: {current_user.name}(ID={current_user.id})')
    
    # 检查用户是否有权限录入该班级的上课记录
    if not can_manage_class(current_user, class_):
        logger.warning(f'[上课记录] 权限不足: 用户={current_user.name}, 班级={class_.name}')
        return jsonify({'message': '权限不足，无法录入该班级的上课记录'}), 403
    
    # 获取班级关联的教师（取第一个作为上课教师）
    class_teachers = class_.class_teachers
    if not class_teachers:
        return jsonify({'message': '该班级没有关联教师，请先添加教师到班级'}), 400
    teacher_id = class_teachers[0].teacher_id
    
    logger.info(f'[上课记录] 班级教师: {class_teachers[0].teacher.name}(ID={teacher_id})')
    
    # 高权限角色可以选择任何教师，普通教师只能选择自己
    if not can_manage_any_teacher(current_user):
        # 普通教师角色只能录入自己绑定的班级
        if current_user.id != teacher_id:
            logger.warning(f'[上课记录] 普通教师权限不足: 用户={current_user.name}, 班级教师={teacher_id}')
            return jsonify({'message': '权限不足，普通教师只能录入自己绑定的班级'}), 403
    
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    
    # 检查教师是否存在
    teacher = User.query.get(teacher_id)
    if not teacher:
        return jsonify({'message': '教师不存在'}), 404
    
    # Parse class_date
    parsed_class_date = parse_date(class_date)
    
    # 创建上课记录
    new_record = ClassRecord(
        class_id=class_id,
        course_id=course_id,
        teacher_id=teacher_id,
        class_date=parsed_class_date,
        start_time=parse_time(start_time),
        end_time=parse_time(end_time),
        hours=hours,
        content=content
    )
    
    db.session.add(new_record)
    db.session.flush()  # 获取记录ID
    
    logger.info(f'[上课记录] 记录创建成功: record_id={new_record.id}')
    
    # 使用同步函数创建考勤记录（自动检查请假状态）
    sync_leave_on_record_creation(new_record)
    
    db.session.commit()
    logger.info(f'[上课记录] 考勤记录处理完成')
    return jsonify({'message': '上课记录创建成功', 'id': new_record.id}), 201

@class_record_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_class_record(id):
    record = ClassRecord.query.get(id)
    if not record:
        return jsonify({'message': '上课记录不存在'}), 404
    
    data = request.get_json()
    record.content = data.get('content', record.content)
    
    # 更新考勤记录
    if 'attendances' in data:
        for attendance_data in data['attendances']:
            attendance = AttendanceRecord.query.filter_by(
                class_record_id=id,
                student_id=attendance_data['student_id']
            ).first()
            if attendance:
                old_status = attendance.status
                new_status = attendance_data['status']
                attendance.status = new_status
                
                # 检查学生加入班级的时间
                from models import ClassStudent
                class_student = ClassStudent.query.filter_by(
                    student_id=attendance_data['student_id'],
                    class_id=record.class_id
                ).first()
                
                join_date = class_student.join_date if class_student else None
                
                # 只有学生加入班级时间小于等于上课时间，才执行课时扣减/恢复
                if join_date and join_date > record.class_date:
                    logger.info(f'[课时] 跳过学生ID={attendance_data["student_id"]}，加入日期 {join_date} 在上课日期 {record.class_date} 之后')
                    continue
                
                # 如果状态从请假变为出勤，扣除课时
                if old_status == '请假' and new_status == '出勤':
                    student_course = StudentCourse.query.filter_by(
                        student_id=attendance_data['student_id'],
                        course_id=record.course_id
                    ).first()
                    if student_course and student_course.remaining_hours > 0:
                        student_course.remaining_hours -= record.hours
                # 如果状态从出勤变为请假，恢复课时
                elif old_status == '出勤' and new_status == '请假':
                    student_course = StudentCourse.query.filter_by(
                        student_id=attendance_data['student_id'],
                        course_id=record.course_id
                    ).first()
                    if student_course:
                        student_course.remaining_hours += record.hours
    
    db.session.commit()
    return jsonify({'message': '上课记录更新成功'})

@class_record_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_class_record(id):
    record = ClassRecord.query.get(id)
    if not record:
        return jsonify({'message': '上课记录不存在'}), 404
    
    # 恢复学生课时
    for attendance in record.attendance_records:
        if attendance.status == '出勤':
            # 检查学生加入班级的时间
            from models import ClassStudent
            class_student = ClassStudent.query.filter_by(
                student_id=attendance.student_id,
                class_id=record.class_id
            ).first()
            
            join_date = class_student.join_date if class_student else None
            
            # 只有学生加入班级时间小于等于上课时间，才恢复课时
            if join_date and join_date > record.class_date:
                logger.info(f'[课时] 跳过学生ID={attendance.student_id}，加入日期 {join_date} 在上课日期 {record.class_date} 之后')
                continue
                
            student_course = StudentCourse.query.filter_by(
                student_id=attendance.student_id,
                course_id=record.course_id
            ).first()
            if student_course:
                student_course.remaining_hours += record.hours
    
    # 删除考勤记录
    AttendanceRecord.query.filter_by(class_record_id=id).delete()
    # 删除上课记录
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '上课记录删除成功'})

@class_record_bp.route('/makeup', methods=['POST'])
@jwt_required()
def create_makeup_record():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    class_date = data.get('class_date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    hours = data.get('hours')
    content = data.get('content')
    
    logger.info(f'[补课记录] 创建请求: student_id={student_id}, course_id={course_id}, date={class_date}, hours={hours}')
    
    # 检查学生是否存在
    student = Student.query.get(student_id)
    if not student:
        logger.error(f'[补课记录] 学生ID={student_id} 不存在')
        return jsonify({'message': '学生不存在'}), 404
    
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        logger.error(f'[补课记录] 课程ID={course_id} 不存在')
        return jsonify({'message': '课程不存在'}), 404
    
    # 检查学生是否有该课程的课时
    student_course = StudentCourse.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    if not student_course:
        logger.error(f'[补课记录] 学生ID={student_id} 没有课程ID={course_id} 的课时')
        return jsonify({'message': '学生没有该课程的课时，请先为学生添加课时'}), 400
    
    if student_course.remaining_hours < hours:
        logger.error(f'[补课记录] 学生ID={student_id} 课时不足，剩余 {student_course.remaining_hours}，需要 {hours}')
        return jsonify({'message': f'学生课时不足，剩余 {student_course.remaining_hours} 课时，需要 {hours} 课时'}), 400
    
    # 获取当前用户作为补课教师
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 为了满足 ClassRecord 表的 class_id 字段要求，我们可以使用一个默认值，或者创建一个特殊的补课班级
    # 这里我们使用 0 作为默认值
    class_id = 0
    
    # Parse class_date
    parsed_class_date = parse_date(class_date)
    
    # 创建补课记录
    new_record = ClassRecord(
        class_id=class_id,
        course_id=course_id,
        teacher_id=current_user_id,
        class_date=parsed_class_date,
        start_time=parse_time(start_time),
        end_time=parse_time(end_time),
        hours=hours,
        content=content,
        is_makeup=True  # 标记为补课
    )
    
    db.session.add(new_record)
    db.session.flush()  # 获取记录ID
    
    logger.info(f'[补课记录] 记录创建成功: record_id={new_record.id}')
    
    # 创建考勤记录，状态为出勤
    new_attendance = AttendanceRecord(
        class_record_id=new_record.id,
        student_id=student_id,
        status='出勤'
    )
    db.session.add(new_attendance)
    
    # 扣除学生课时
    student_course.remaining_hours -= hours
    logger.info(f'[补课记录] 扣除学生ID={student_id} 课时 {hours}，剩余 {student_course.remaining_hours}')
    
    db.session.commit()
    logger.info(f'[补课记录] 处理完成')
    return jsonify({'message': '补课记录创建成功', 'id': new_record.id}), 201
