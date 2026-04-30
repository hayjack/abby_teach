from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import ClassRecord, AttendanceRecord, LeaveRecord, Student, User, Course, StudentCourse
from extensions import db
from datetime import date, datetime, timedelta
from utils import parse_date

report_bp = Blueprint('report', __name__)

@report_bp.route('/student_attendance', methods=['GET'])
@jwt_required()
def get_student_attendance():
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id)
    
    # 只有当提供了日期参数时，才添加日期过滤条件
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    if class_id:
        query = query.filter(ClassRecord.class_id == class_id)
    
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    attendances = query.all()
    
    stats = {}
    for attendance in attendances:
        sid = attendance.student_id
        if sid not in stats:
            # 空值检查
            student_name = '未知学生'
            if attendance.student:
                student_name = attendance.student.name
                if attendance.student.english_name:
                    student_name = f"{attendance.student.name} ({attendance.student.english_name})"
            stats[sid] = {
                'student_name': student_name,
                'total': 0,
                'present': 0,
                'leave': 0,
                'absent': 0
            }
        stats[sid]['total'] += 1
        if attendance.status == '出勤':
            stats[sid]['present'] += 1
        elif attendance.status == '请假':
            stats[sid]['leave'] += 1
        else:
            stats[sid]['absent'] += 1
    
    return jsonify(list(stats.values()))

@report_bp.route('/teacher_classes', methods=['GET'])
@jwt_required()
def get_teacher_classes():
    teacher_id = request.args.get('teacher_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = ClassRecord.query
    
    # 只有当提供了日期参数时，才添加日期过滤条件
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    if teacher_id:
        query = query.filter(ClassRecord.teacher_id == teacher_id)
    
    records = query.all()
    
    stats = {}
    for record in records:
        tid = record.teacher_id
        if tid not in stats:
            # 空值检查
            teacher_name = '未知教师'
            if record.teacher:
                teacher_name = record.teacher.name
            stats[tid] = {
                'teacher_name': teacher_name,
                'total_classes': 0,
                'total_hours': 0
            }
        stats[tid]['total_classes'] += 1
        stats[tid]['total_hours'] += float(record.hours) if record.hours else 0
    
    return jsonify(list(stats.values()))

@report_bp.route('/course_attendance', methods=['GET'])
@jwt_required()
def get_course_attendance():
    course_id = request.args.get('course_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id)
    
    # 只有当提供了日期参数时，才添加日期过滤条件
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    if course_id:
        query = query.filter(ClassRecord.course_id == course_id)
    
    attendances = query.all()
    
    stats = {}
    for attendance in attendances:
        class_record = attendance.class_record
        cid = class_record.course_id if class_record else None
        if cid and cid not in stats:
            # 空值检查
            course_name = '未知课程'
            if class_record and class_record.course:
                course_name = class_record.course.name
            stats[cid] = {
                'course_name': course_name,
                'total': 0,
                'present': 0,
                'leave': 0,
                'absent': 0
            }
        if cid:
            stats[cid]['total'] += 1
            if attendance.status == '出勤':
                stats[cid]['present'] += 1
            elif attendance.status == '请假':
                stats[cid]['leave'] += 1
            else:
                stats[cid]['absent'] += 1
    
    return jsonify(list(stats.values()))

@report_bp.route('/class_attendance', methods=['GET'])
@jwt_required()
def get_class_attendance():
    class_id = request.args.get('class_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id)
    
    # 只有当提供了日期参数时，才添加日期过滤条件
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    if class_id:
        query = query.filter(ClassRecord.class_id == class_id)
    
    attendances = query.all()
    
    stats = {}
    for attendance in attendances:
        class_record = attendance.class_record
        cid = class_record.class_id if class_record else None
        if cid and cid not in stats:
            # 空值检查
            class_name = '未知班级'
            if class_record and class_record.class_:
                class_name = class_record.class_.name
            stats[cid] = {
                'class_name': class_name,
                'total': 0,
                'present': 0,
                'leave': 0,
                'absent': 0
            }
        if cid:
            stats[cid]['total'] += 1
            if attendance.status == '出勤':
                stats[cid]['present'] += 1
            elif attendance.status == '请假':
                stats[cid]['leave'] += 1
            else:
                stats[cid]['absent'] += 1
    
    return jsonify(list(stats.values()))

@report_bp.route('/student-hours', methods=['GET'])
@jwt_required()
def get_student_hours():
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 查询参数
    student_name = request.args.get('student_name')
    course_id = request.args.get('course_id')
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    
    query = db.session.query(
        Student.id,
        Student.name,
        Student.english_name,
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        StudentCourse.total_hours,
        StudentCourse.remaining_hours
    ).join(
        StudentCourse, Student.id == StudentCourse.student_id
    ).join(
        Course, StudentCourse.course_id == Course.id
    )
    
    # 应用学生ID过滤条件
    if student_id:
        query = query.filter(Student.id == student_id)
    
    # 应用学生姓名过滤条件
    if student_name:
        query = query.filter(Student.name.ilike(f'%{student_name}%'))
    
    # 应用课程ID过滤条件
    if course_id:
        query = query.filter(Course.id == course_id)
    
    # 应用班级ID过滤条件
    if class_id:
        from models import ClassStudent
        # 获取该班级的所有学生ID
        class_students = ClassStudent.query.filter(ClassStudent.class_id == class_id).all()
        student_ids = [cs.student_id for cs in class_students]
        if student_ids:
            query = query.filter(Student.id.in_(student_ids))
    
    # 获取分页数据
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 构建响应数据
    items = []
    for result in pagination.items:
        student_name_display = result.name
        if result.english_name:
            student_name_display = f"{result.name} ({result.english_name})"
        
        items.append({
            'student_id': result.id,
            'student_name': student_name_display,
            'course_id': result.course_id,
            'course_name': result.course_name,
            'total_hours': result.total_hours,
            'remaining_hours': result.remaining_hours,
            'used_hours': result.total_hours - result.remaining_hours
        })
    
    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page
    })

@report_bp.route('/student_attendance_detail', methods=['GET'])
@jwt_required()
def get_student_attendance_detail():
    """
    获取学生上课记录明细，用于报表统计
    支持按学生ID、班级ID、日期范围筛选
    """
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id)
    
    # 只有当提供了日期参数时，才添加日期过滤条件
    if start_date:
        query = query.filter(ClassRecord.class_date >= parse_date(start_date))
    if end_date:
        query = query.filter(ClassRecord.class_date <= parse_date(end_date))
    
    if class_id:
        query = query.filter(ClassRecord.class_id == class_id)
    
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    # 按上课日期倒序排序
    attendances = query.order_by(ClassRecord.class_date.desc()).all()
    
    # 构建响应数据
    result = []
    for attendance in attendances:
        class_record = attendance.class_record
        # 空值检查
        student_name = '未知学生'
        if attendance.student:
            student_name = attendance.student.name
        
        class_name = '未知班级'
        if class_record and class_record.class_:
            class_name = class_record.class_.name
        
        course_name = '未知课程'
        if class_record and class_record.course:
            course_name = class_record.course.name
        
        teacher_name = '未知教师'
        if class_record and class_record.teacher:
            teacher_name = class_record.teacher.name
        
        result.append({
            'id': attendance.id,
            'student_id': attendance.student_id,
            'student_name': student_name,
            'class_name': class_name,
            'course_id': class_record.course_id if class_record else None,
            'course_name': course_name,
            'teacher_name': teacher_name,
            'class_date': class_record.class_date.isoformat() if class_record and class_record.class_date else None,
            'start_time': class_record.start_time.isoformat() if class_record and class_record.start_time else None,
            'end_time': class_record.end_time.isoformat() if class_record and class_record.end_time else None,
            'hours': float(class_record.hours) if class_record and class_record.hours else 0,
            'status': attendance.status,
            'is_attended': attendance.status == '出勤'
        })
    
    return jsonify(result)

@report_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """
    获取首页统计数据
    """
    # 获取学生总数
    student_count = Student.query.count()
    
    # 获取班级总数
    from models import Class
    class_count = Class.query.count()
    
    # 获取课程总数
    course_count = Course.query.count()
    
    # 获取本月上课次数
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    class_record_count = ClassRecord.query.filter(
        ClassRecord.class_date >= start_of_month
    ).count()
    
    # 获取学生出勤情况
    attendance_stats = {
        'present': 0,
        'leave': 0,
        'absent': 0
    }
    
    recent_attendances = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id).filter(
        ClassRecord.class_date >= start_of_month
    ).all()
    
    for attendance in recent_attendances:
        if attendance.status == '出勤':
            attendance_stats['present'] += 1
        elif attendance.status == '请假':
            attendance_stats['leave'] += 1
        else:
            attendance_stats['absent'] += 1
    
    # 获取教师上课统计
    teacher_stats = {}
    recent_class_records = ClassRecord.query.filter(
        ClassRecord.class_date >= start_of_month
    ).all()
    
    for record in recent_class_records:
        tid = record.teacher_id
        if tid not in teacher_stats:
            teacher_stats[tid] = {
                'teacher_name': record.teacher.name,
                'class_count': 0
            }
        teacher_stats[tid]['class_count'] += 1
    
    # 转换教师统计为列表
    teacher_stats_list = list(teacher_stats.values())
    # 按上课次数排序，取前5名
    teacher_stats_list.sort(key=lambda x: x['class_count'], reverse=True)
    top_teachers = teacher_stats_list[:5]
    
    return jsonify({
        'student_count': student_count,
        'class_count': class_count,
        'course_count': course_count,
        'class_record_count': class_record_count,
        'attendance_stats': attendance_stats,
        'top_teachers': top_teachers
    })
