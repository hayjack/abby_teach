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
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id).filter(
        ClassRecord.class_date >= parse_date(start_date),
        ClassRecord.class_date <= parse_date(end_date)
    )
    
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    attendances = query.all()
    
    stats = {}
    for attendance in attendances:
        sid = attendance.student_id
        if sid not in stats:
            stats[sid] = {
                'student_name': attendance.student.name,
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
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    query = ClassRecord.query.filter(
        ClassRecord.class_date >= parse_date(start_date),
        ClassRecord.class_date <= parse_date(end_date)
    )
    
    if teacher_id:
        query = query.filter(ClassRecord.teacher_id == teacher_id)
    
    records = query.all()
    
    stats = {}
    for record in records:
        tid = record.teacher_id
        if tid not in stats:
            stats[tid] = {
                'teacher_name': record.teacher.name,
                'total_classes': 0,
                'total_hours': 0
            }
        stats[tid]['total_classes'] += 1
        stats[tid]['total_hours'] += float(record.hours)
    
    return jsonify(list(stats.values()))

@report_bp.route('/course_attendance', methods=['GET'])
@jwt_required()
def get_course_attendance():
    course_id = request.args.get('course_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id).filter(
        ClassRecord.class_date >= parse_date(start_date),
        ClassRecord.class_date <= parse_date(end_date)
    )
    
    if course_id:
        query = query.filter(ClassRecord.course_id == course_id)
    
    attendances = query.all()
    
    stats = {}
    for attendance in attendances:
        cid = attendance.class_record.course_id
        if cid not in stats:
            stats[cid] = {
                'course_name': attendance.class_record.course.name,
                'total': 0,
                'present': 0,
                'leave': 0,
                'absent': 0
            }
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
    student_id = request.args.get('student_id')
    
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
    
    if student_id:
        query = query.filter(Student.id == student_id)
    
    results = query.all()
    
    stats = []
    for result in results:
        # 构建学生名字：中文名(英文名)
        student_name = result.name
        if result.english_name:
            student_name = f"{result.name} ({result.english_name})"
        
        stats.append({
            'student_id': result.id,
            'student_name': student_name,
            'course_id': result.course_id,
            'course_name': result.course_name,
            'total_hours': result.total_hours,
            'remaining_hours': result.remaining_hours,
            'used_hours': result.total_hours - result.remaining_hours
        })
    
    return jsonify(stats)

@report_bp.route('/student_attendance_detail', methods=['GET'])
@jwt_required()
def get_student_attendance_detail():
    """
    获取学生上课记录明细，用于报表统计
    支持按学生ID、日期范围筛选
    """
    student_id = request.args.get('student_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    query = AttendanceRecord.query.join(ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id).filter(
        ClassRecord.class_date >= parse_date(start_date),
        ClassRecord.class_date <= parse_date(end_date)
    )
    
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    # 按上课日期倒序排序
    attendances = query.order_by(ClassRecord.class_date.desc()).all()
    
    # 构建响应数据
    result = []
    for attendance in attendances:
        class_record = attendance.class_record
        result.append({
            'id': attendance.id,
            'student_id': attendance.student_id,
            'student_name': attendance.student.name,
            'class_name': class_record.class_.name,
            'course_name': class_record.course.name,
            'teacher_name': class_record.teacher.name,
            'class_date': class_record.class_date.isoformat(),
            'start_time': class_record.start_time.isoformat(),
            'end_time': class_record.end_time.isoformat(),
            'hours': float(class_record.hours),
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
