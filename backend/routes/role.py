from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Role, RoleMenu
from extensions import db

role_bp = Blueprint('role', __name__)

@role_bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    return jsonify([{
        'id': role.id,
        'name': role.name,
        'priority': role.priority
    } for role in roles])

@role_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({'message': '角色不存在'}), 404
    
    menu_ids = [rm.menu_id for rm in role.role_menus]
    
    return jsonify({
        'id': role.id,
        'name': role.name,
        'priority': role.priority,
        'menu_ids': menu_ids
    })

@role_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    data = request.get_json()
    name = data.get('name')
    priority = data.get('priority', 0)
    
    if Role.query.filter_by(name=name).first():
        return jsonify({'message': '角色名称已存在'}), 400
    
    new_role = Role(name=name, priority=priority)
    db.session.add(new_role)
    db.session.commit()
    
    return jsonify({'message': '角色创建成功', 'id': new_role.id}), 201

@role_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({'message': '角色不存在'}), 404
    
    data = request.get_json()
    role.name = data.get('name', role.name)
    role.priority = data.get('priority', role.priority)
    
    if 'menu_ids' in data:
        RoleMenu.query.filter_by(role_id=id).delete()
        for menu_id in data['menu_ids']:
            role_menu = RoleMenu(role_id=id, menu_id=menu_id)
            db.session.add(role_menu)
    
    db.session.commit()
    return jsonify({'message': '角色更新成功'})

@role_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({'message': '角色不存在'}), 404
    
    RoleMenu.query.filter_by(role_id=id).delete()
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': '角色删除成功'})
