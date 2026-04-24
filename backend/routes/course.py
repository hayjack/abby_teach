from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Course
from extensions import db

course_bp = Blueprint('course', __name__)

@course_bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'id': course.id,
        'course_id': course.id,
        'name': course.name,
        'course_name': course.name,
        'total_hours': float(course.total_hours),
        'description': course.description
    } for course in courses])

@course_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    return jsonify({
        'id': course.id,
        'course_id': course.id,
        'name': course.name,
        'course_name': course.name,
        'total_hours': float(course.total_hours),
        'description': course.description
    })

@course_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json()
    name = data.get('name')
    total_hours = data.get('total_hours', 0)
    description = data.get('description')
    
    new_course = Course(name=name, total_hours=total_hours, description=description)
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({'message': '课程创建成功', 'id': new_course.id}), 201

@course_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    
    data = request.get_json()
    course.name = data.get('name', course.name)
    course.total_hours = data.get('total_hours', course.total_hours)
    course.description = data.get('description', course.description)
    
    db.session.commit()
    return jsonify({'message': '课程更新成功'})

@course_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({'message': '课程不存在'}), 404
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': '课程删除成功'})
