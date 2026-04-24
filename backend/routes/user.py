from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import User, Role, UserRole
from extensions import db
from passlib.hash import pbkdf2_sha256

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'english_name': user.english_name,
            'phone': user.phone,
            'roles': [{'id': r.id, 'name': r.name} for r in user.roles]
        })
    return jsonify(result)

@user_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'english_name': user.english_name,
        'phone': user.phone,
        'roles': [r.id for r in user.roles],
        'role_list': [{'id': r.id, 'name': r.name} for r in user.roles]
    })

@user_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    english_name = data.get('english_name')
    phone = data.get('phone')
    role_ids = data.get('role_ids', [])
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    hashed_password = pbkdf2_sha256.hash(password)
    new_user = User(
        username=username,
        password=hashed_password,
        name=name,
        english_name=english_name,
        phone=phone
    )
    
    db.session.add(new_user)
    db.session.flush()
    
    for role_id in role_ids:
        role = Role.query.get(role_id)
        if role:
            user_role = UserRole(user_id=new_user.id, role_id=role_id)
            db.session.add(user_role)
    
    db.session.commit()
    
    return jsonify({'message': '用户创建成功', 'id': new_user.id}), 201

@user_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.english_name = data.get('english_name', user.english_name)
    user.phone = data.get('phone', user.phone)
    
    if 'password' in data and data['password']:
        user.password = pbkdf2_sha256.hash(data['password'])
    
    if 'role_ids' in data:
        UserRole.query.filter_by(user_id=id).delete()
        for role_id in data['role_ids']:
            role = Role.query.get(role_id)
            if role:
                user_role = UserRole(user_id=id, role_id=role_id)
                db.session.add(user_role)
    
    db.session.commit()
    return jsonify({'message': '用户更新成功'})

@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    UserRole.query.filter_by(user_id=id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '用户删除成功'})

@user_bp.route('/<int:user_id>/roles/<int:role_id>', methods=['POST'])
@jwt_required()
def add_user_role(user_id, role_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'message': '角色不存在'}), 404
    
    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if existing:
        return jsonify({'message': '该用户已有此角色'}), 400
    
    new_ur = UserRole(user_id=user_id, role_id=role_id)
    db.session.add(new_ur)
    db.session.commit()
    return jsonify({'message': '角色添加成功'})

@user_bp.route('/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def remove_user_role(user_id, role_id):
    ur = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if not ur:
        return jsonify({'message': '该用户没有此角色'}), 404
    
    db.session.delete(ur)
    db.session.commit()
    return jsonify({'message': '角色移除成功'})
