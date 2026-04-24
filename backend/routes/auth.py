from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Role, UserRole
from extensions import db
from passlib.hash import pbkdf2_sha256

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not pbkdf2_sha256.verify(password, user.password):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'roles': [r.id for r in user.roles],
            'role_names': [r.name for r in user.roles]
        }
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    english_name = data.get('english_name')
    phone = data.get('phone')
    role_ids = data.get('role_ids', [2])  # 默认角色为教师
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 创建新用户
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
    
    # 分配角色
    for role_id in role_ids:
        role = Role.query.get(role_id)
        if role:
            ur = UserRole(user_id=new_user.id, role_id=role_id)
            db.session.add(ur)
    
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'english_name': user.english_name,
        'phone': user.phone,
        'roles': [r.id for r in user.roles],
        'role_names': [r.name for r in user.roles]
    })
