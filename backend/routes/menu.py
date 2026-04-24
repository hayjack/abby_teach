from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Menu
from extensions import db

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/', methods=['GET'])
def get_menus():
    menus = Menu.query.all()
    return jsonify([{
        'id': menu.id,
        'name': menu.name,
        'path': menu.path,
        'parent_id': menu.parent_id,
        'icon': menu.icon,
        'order': menu.order
    } for menu in menus])

@menu_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_menu(id):
    menu = Menu.query.get(id)
    if not menu:
        return jsonify({'message': '菜单不存在'}), 404
    return jsonify({
        'id': menu.id,
        'name': menu.name,
        'path': menu.path,
        'parent_id': menu.parent_id,
        'icon': menu.icon,
        'order': menu.order
    })

@menu_bp.route('/', methods=['POST'])
@jwt_required()
def create_menu():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')
    parent_id = data.get('parent_id')
    icon = data.get('icon')
    order = data.get('order', 0)
    
    new_menu = Menu(
        name=name,
        path=path,
        parent_id=parent_id,
        icon=icon,
        order=order
    )
    
    db.session.add(new_menu)
    db.session.commit()
    
    return jsonify({'message': '菜单创建成功', 'id': new_menu.id}), 201

@menu_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_menu(id):
    menu = Menu.query.get(id)
    if not menu:
        return jsonify({'message': '菜单不存在'}), 404
    
    data = request.get_json()
    menu.name = data.get('name', menu.name)
    menu.path = data.get('path', menu.path)
    menu.parent_id = data.get('parent_id', menu.parent_id)
    menu.icon = data.get('icon', menu.icon)
    menu.order = data.get('order', menu.order)
    
    db.session.commit()
    return jsonify({'message': '菜单更新成功'})

@menu_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_menu(id):
    menu = Menu.query.get(id)
    if not menu:
        return jsonify({'message': '菜单不存在'}), 404
    
    if menu.children:
        return jsonify({'message': '该菜单有子菜单，无法删除'}), 400
    
    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': '菜单删除成功'})
