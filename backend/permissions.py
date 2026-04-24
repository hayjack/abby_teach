from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User, Role

# 角色优先级定义（数字越大，权限越高）
# 这里作为默认值，实际优先使用数据库中的 priority 字段
ROLE_PRIORITY = {
    '管理员': 100,
    '校长': 80,
    '教学主管': 60,
    '教师': 20,
}

def get_user_highest_priority_role(user):
    """
    获取用户最高优先级的角色
    返回: (role_name, priority)
    
    优先使用数据库中的 priority 字段，如果没有则使用硬编码的默认值
    """
    if not user.roles:
        return None, 0
    
    highest_role = None
    highest_priority = 0
    
    for role in user.roles:
        # 优先使用数据库中的 priority 字段
        if role.priority and role.priority > 0:
            priority = role.priority
        else:
            # 回退到硬编码的默认优先级
            priority = ROLE_PRIORITY.get(role.name, 0)
        
        if priority > highest_priority:
            highest_priority = priority
            highest_role = role.name
    
    return highest_role, highest_priority

def can_manage_any_teacher(user):
    """
    检查用户是否有权限录入任何教师的上课记录
    管理员、校长、教学主管可以录入任何教师的上课记录
    """
    _, priority = get_user_highest_priority_role(user)
    # 获取教学主管的优先级（优先从数据库查询，否则使用默认值）
    principal_role = Role.query.filter_by(name='教学主管').first()
    threshold = principal_role.priority if principal_role and principal_role.priority > 0 else ROLE_PRIORITY.get('教学主管', 60)
    return priority >= threshold

def can_manage_class(user, class_):
    """
    检查用户是否有权限录入指定班级的上课记录
    管理员、校长、教学主管可以录入任何班级
    教师只能录入自己绑定的班级
    """
    _, priority = get_user_highest_priority_role(user)
    
    # 获取教学主管的优先级阈值
    principal_role = Role.query.filter_by(name='教学主管').first()
    threshold = principal_role.priority if principal_role and principal_role.priority > 0 else ROLE_PRIORITY.get('教学主管', 60)
    
    # 高权限角色可以管理任何班级
    if priority >= threshold:
        return True
    
    # 教师只能管理自己绑定的班级
    teacher_role = Role.query.filter_by(name='教师').first()
    teacher_threshold = teacher_role.priority if teacher_role and teacher_role.priority > 0 else ROLE_PRIORITY.get('教师', 20)
    
    if priority >= teacher_threshold:
        class_teachers = [ct.teacher_id for ct in class_.class_teachers]
        return user.id in class_teachers
    
    return False

def require_manage_any_teacher(f):
    """
    装饰器：要求用户有权限录入任何教师的上课记录
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        if not can_manage_any_teacher(user):
            return jsonify({'message': '权限不足，无法录入其他教师的上课记录'}), 403
        
        return f(*args, **kwargs)
    return decorated

def require_manage_class(class_id_arg='class_id'):
    """
    装饰器：要求用户有权限录入指定班级的上课记录
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from models import Class
            
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 获取班级ID（从请求参数或JSON数据中）
            from flask import request
            class_id = kwargs.get(class_id_arg) or request.args.get(class_id_arg)
            if not class_id:
                data = request.get_json()
                class_id = data.get(class_id_arg) if data else None
            
            if not class_id:
                return jsonify({'message': '缺少班级ID参数'}), 400
            
            class_ = Class.query.get(class_id)
            if not class_:
                return jsonify({'message': '班级不存在'}), 404
            
            if not can_manage_class(user, class_):
                return jsonify({'message': '权限不足，无法录入该班级的上课记录'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
