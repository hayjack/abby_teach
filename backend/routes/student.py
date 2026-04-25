from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Student, StudentCourse, Course
from extensions import db
from datetime import date
from utils import parse_date

student_bp = Blueprint('student', __name__)

@student_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取分页数据
    pagination = Student.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 构建响应数据
    students = []
    for student in pagination.items:
        students.append({
            'id': student.id,
            'name': student.name,
            'english_name': student.english_name,
            'gender': student.gender,
            'birthday': student.birthday.isoformat() if student.birthday else None,
            'parent_name': student.parent_name,
            'parent_phone': student.parent_phone,
            'address': student.address
        })
    
    return jsonify({
        'items': students,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@student_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    courses = []
    for sc in student.student_courses:
        courses.append({
            'course_id': sc.course_id,
            'course_name': sc.course.name,
            'total_hours': sc.total_hours,
            'remaining_hours': sc.remaining_hours,
            'start_date': sc.start_date.isoformat() if sc.start_date else None,
            'end_date': sc.end_date.isoformat() if sc.end_date else None
        })
    
    return jsonify({
        'id': student.id,
        'name': student.name,
        'english_name': student.english_name,
        'gender': student.gender,
        'birthday': student.birthday.isoformat() if student.birthday else None,
        'parent_name': student.parent_name,
        'parent_phone': student.parent_phone,
        'address': student.address,
        'courses': courses
    })

@student_bp.route('/', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json()
    name = data.get('name')
    english_name = data.get('english_name')
    gender = data.get('gender')
    birthday = data.get('birthday')
    parent_name = data.get('parent_name')
    parent_phone = data.get('parent_phone')
    address = data.get('address')
    
    new_student = Student(
        name=name,
        english_name=english_name,
        gender=gender,
        birthday=parse_date(birthday),
        parent_name=parent_name,
        parent_phone=parent_phone,
        address=address
    )
    
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({'message': '学生创建成功', 'id': new_student.id}), 201

@student_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    data = request.get_json()
    student.name = data.get('name', student.name)
    student.english_name = data.get('english_name', student.english_name)
    student.gender = data.get('gender', student.gender)
    if 'birthday' in data:
        student.birthday = parse_date(data['birthday'])
    student.parent_name = data.get('parent_name', student.parent_name)
    student.parent_phone = data.get('parent_phone', student.parent_phone)
    student.address = data.get('address', student.address)
    
    db.session.commit()
    return jsonify({'message': '学生更新成功'})

@student_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    StudentCourse.query.filter_by(student_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': '学生删除成功'})

@student_bp.route('/<int:id>/attendance', methods=['GET'])
@jwt_required()
def get_student_attendance(id):
    """
    获取学生的上课记录（考勤记录）
    """
    from models import AttendanceRecord, ClassRecord, Course, User, Class, Student
    
    # 检查学生是否存在
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    # 获取学生的所有考勤记录，按上课日期倒序排序
    attendances = AttendanceRecord.query.filter_by(student_id=id).join(
        ClassRecord, AttendanceRecord.class_record_id == ClassRecord.id
    ).order_by(ClassRecord.class_date.desc()).all()
    
    # 构建学生名字：中文名(英文名)
    student_name = student.name
    if student.english_name:
        student_name = f"{student.name} ({student.english_name})"
    
    # 构建响应数据
    result = []
    for attendance in attendances:
        class_record = attendance.class_record
        result.append({
            'id': attendance.id,
            'class_record_id': class_record.id,
            'student_id': student.id,
            'student_name': student_name,
            'class_name': class_record.class_.name,
            'course_name': class_record.course.name,
            'teacher_name': class_record.teacher.name,
            'class_date': class_record.class_date.isoformat(),
            'start_time': class_record.start_time.isoformat(),
            'end_time': class_record.end_time.isoformat(),
            'hours': float(class_record.hours),
            'status': attendance.status,
            'is_attended': attendance.status == '出勤',
            'created_at': attendance.created_at.isoformat()
        })
    
    return jsonify(result)

@student_bp.route('/<int:id>/courses', methods=['POST'])
@jwt_required()
def add_student_course(id):
    """
    给学生增加课时
    """
    # 检查学生是否存在
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    # 获取请求数据
    data = request.get_json()
    course_id = data.get('course_id')
    # 接受 total_hours 或 hours 字段
    hours = data.get('total_hours', data.get('hours', 0))
    start_date = parse_date(data.get('start_date'))
    end_date = parse_date(data.get('end_date'))
    
    # 检查课程是否存在
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    
    # 检查学生是否已经有该课程的记录
    student_course = StudentCourse.query.filter_by(
        student_id=id, 
        course_id=course_id
    ).first()
    
    if student_course:
        # 如果已有记录，更新剩余课时
        student_course.remaining_hours += hours
        student_course.total_hours += hours
        # 更新开始和结束日期（如果提供）
        if start_date:
            student_course.start_date = start_date
        if end_date:
            student_course.end_date = end_date
    else:
        # 如果没有记录，创建新的学生课程记录
        student_course = StudentCourse(
            student_id=id,
            course_id=course_id,
            total_hours=hours,
            remaining_hours=hours,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(student_course)
    
    # 提交数据库更改
    db.session.commit()
    
    return jsonify({'message': '课时添加成功'})
