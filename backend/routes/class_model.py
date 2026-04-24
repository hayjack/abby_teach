from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Class, ClassTeacher, ClassStudent, Student, User
from extensions import db

class_bp = Blueprint('class_model', __name__)

@class_bp.route('/', methods=['GET'])
@jwt_required()
def get_classes():
    classes = Class.query.all()
    return jsonify([{
        'id': class_.id,
        'name': class_.name,
        'teacher_ids': [ct.teacher_id for ct in class_.class_teachers],
        'teacher_names': [ct.teacher.name for ct in class_.class_teachers],
        'student_count': len(class_.class_students),
        'created_at': class_.created_at.isoformat()
    } for class_ in classes])

@class_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_class(id):
    class_ = Class.query.get(id)
    if not class_:
        return jsonify({'message': '班级不存在'}), 404
    
    students = []
    for cs in class_.class_students:
        students.append({
            'student_id': cs.student_id,
            'student_name': cs.student.name,
            'joined_date': cs.joined_date.isoformat() if cs.joined_date else None
        })
    
    teachers = []
    for ct in class_.class_teachers:
        teachers.append({
            'teacher_id': ct.teacher_id,
            'teacher_name': ct.teacher.name,
            'joined_date': ct.joined_date.isoformat() if ct.joined_date else None
        })
    
    return jsonify({
        'id': class_.id,
        'name': class_.name,
        'students': students,
        'teachers': teachers
    })

@class_bp.route('/', methods=['POST'])
@jwt_required()
def create_class():
    data = request.get_json()
    name = data.get('name')
    teacher_ids = data.get('teacher_ids', [])
    
    new_class = Class(name=name)
    
    db.session.add(new_class)
    db.session.flush()
    
    for teacher_id in teacher_ids:
        teacher = User.query.get(teacher_id)
        if teacher:
            ct = ClassTeacher(class_id=new_class.id, teacher_id=teacher_id)
            db.session.add(ct)
    
    db.session.commit()
    
    return jsonify({'message': '班级创建成功', 'id': new_class.id}), 201

@class_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_class(id):
    class_ = Class.query.get(id)
    if not class_:
        return jsonify({'message': '班级不存在'}), 404
    
    data = request.get_json()
    class_.name = data.get('name', class_.name)
    
    if 'teacher_ids' in data:
        ClassTeacher.query.filter_by(class_id=id).delete()
        for teacher_id in data['teacher_ids']:
            teacher = User.query.get(teacher_id)
            if teacher:
                ct = ClassTeacher(class_id=id, teacher_id=teacher_id)
                db.session.add(ct)
    
    db.session.commit()
    return jsonify({'message': '班级更新成功'})

@class_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_class(id):
    class_ = Class.query.get(id)
    if not class_:
        return jsonify({'message': '班级不存在'}), 404
    
    ClassTeacher.query.filter_by(class_id=id).delete()
    ClassStudent.query.filter_by(class_id=id).delete()
    db.session.delete(class_)
    db.session.commit()
    return jsonify({'message': '班级删除成功'})

@class_bp.route('/<int:class_id>/students', methods=['GET'])
@jwt_required()
def get_class_students(class_id):
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({'message': '班级不存在'}), 404
    
    students = []
    for cs in class_.class_students:
        students.append({
            'id': cs.student.id,
            'name': cs.student.name,
            'english_name': cs.student.english_name,
            'parent_phone': cs.student.parent_phone
        })
    
    return jsonify(students)

@class_bp.route('/<int:class_id>/students', methods=['POST'])
@jwt_required()
def add_class_student(class_id):
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({'message': '班级不存在'}), 404
    
    data = request.get_json()
    student_id = data.get('student_id')
    
    existing = ClassStudent.query.filter_by(class_id=class_id, student_id=student_id).first()
    if existing:
        return jsonify({'message': '该学生已在班级中'}), 400
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    new_cs = ClassStudent(class_id=class_id, student_id=student_id)
    db.session.add(new_cs)
    db.session.commit()
    return jsonify({'message': '学生添加成功'})

@class_bp.route('/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def remove_class_student(class_id, student_id):
    cs = ClassStudent.query.filter_by(class_id=class_id, student_id=student_id).first()
    if not cs:
        return jsonify({'message': '该学生不在班级中'}), 404
    
    db.session.delete(cs)
    db.session.commit()
    return jsonify({'message': '学生移除成功'})
