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
    students = Student.query.all()
    return jsonify([{
        'id': student.id,
        'name': student.name,
        'english_name': student.english_name,
        'gender': student.gender,
        'birthday': student.birthday.isoformat() if student.birthday else None,
        'parent_name': student.parent_name,
        'parent_phone': student.parent_phone,
        'address': student.address
    } for student in students])

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

@student_bp.route('/<int:id>/courses', methods=['POST'])
@jwt_required()
def add_student_course(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    data = request.get_json()
    course_id = data.get('course_id')
    total_hours = data.get('total_hours')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    
    existing = StudentCourse.query.filter_by(student_id=id, course_id=course_id).first()
    if existing:
        existing.total_hours += total_hours
        existing.remaining_hours += total_hours
        existing.start_date = parse_date(start_date) if start_date else existing.start_date
        existing.end_date = parse_date(end_date) if end_date else existing.end_date
    else:
        new_student_course = StudentCourse(
            student_id=id,
            course_id=course_id,
            total_hours=total_hours,
            remaining_hours=total_hours,
            start_date=parse_date(start_date),
            end_date=parse_date(end_date)
        )
        db.session.add(new_student_course)
    
    db.session.commit()
    return jsonify({'message': '课程添加成功'})
