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
    
    query = AttendanceRecord.query.join(ClassRecord).filter(
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
    
    query = AttendanceRecord.query.join(ClassRecord).filter(
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
        stats.append({
            'student_id': result.id,
            'student_name': result.name,
            'course_id': result.course_id,
            'course_name': result.course_name,
            'total_hours': result.total_hours,
            'remaining_hours': result.remaining_hours,
            'used_hours': result.total_hours - result.remaining_hours
        })
    
    return jsonify(stats)
