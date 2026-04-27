from app import app, db
from models.user import User
from models.role import Role
from models.menu import Menu
from models.user_role import UserRole
from passlib.hash import pbkdf2_sha256

with app.app_context():
    # 创建角色（如果不存在）
    roles_config = [
        {'name': '管理员', 'priority': 100},
        {'name': '校长', 'priority': 80},
        {'name': '教学主管', 'priority': 60},
        {'name': '教师', 'priority': 20},
    ]
    
    roles = {}
    for role_config in roles_config:
        role = Role.query.filter_by(name=role_config['name']).first()
        if not role:
            role = Role(name=role_config['name'], priority=role_config['priority'])
            db.session.add(role)
            db.session.flush()
            print(f'[OK] Created role: {role_config["name"]} (priority: {role_config["priority"]})')
        else:
            # Update priority if needed
            if role.priority != role_config['priority']:
                role.priority = role_config['priority']
                print(f'[OK] Updated priority for role: {role_config["name"]} to {role_config["priority"]}')
            else:
                print(f'[SKIP] Role already exists: {role_config["name"]}')
        roles[role_config['name']] = role
    
    # 创建管理员账号（如果不存在）- 使用多角色方式
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=pbkdf2_sha256.hash('admin123'),
            name='系统管理员',
            english_name='Admin',
            phone='13800138000'
        )
        db.session.add(admin)
        db.session.flush()
        
        # 为管理员分配角色
        ur = UserRole(user_id=admin.id, role_id=roles['管理员'].id)
        db.session.add(ur)
        print('[OK] Created user: admin with role: 管理员')
    else:
        # 检查是否已有角色关联，没有则添加
        existing_ur = UserRole.query.filter_by(user_id=admin.id, role_id=roles['管理员'].id).first()
        if not existing_ur:
            ur = UserRole(user_id=admin.id, role_id=roles['管理员'].id)
            db.session.add(ur)
            print('[OK] Added admin role to user: admin')
        else:
            print('[SKIP] User already exists: admin')
    
    # 创建基础菜单（如果不存在）
    menus = [
        {'name': '系统管理', 'path': '/system', 'parent_id': None, 'icon': 'Setting', 'order': 1},
        {'name': '教师管理', 'path': '/system/users', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '角色管理', 'path': '/system/roles', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '菜单管理', 'path': '/system/menus', 'parent_id': None, 'icon': None, 'order': 3},
        {'name': '学生管理', 'path': '/student', 'parent_id': None, 'icon': 'User', 'order': 2},
        {'name': '学生信息', 'path': '/student/list', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '缴费记录', 'path': '/student/payment', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '课时管理', 'path': '/student/course', 'parent_id': None, 'icon': None, 'order': 3},
        {'name': '班级管理', 'path': '/class', 'parent_id': None, 'icon': 'FolderOpened', 'order': 3},
        {'name': '班级信息', 'path': '/class/list', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '班级学生', 'path': '/class/students', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '班级教师', 'path': '/class/teachers', 'parent_id': None, 'icon': None, 'order': 3},
        {'name': '课程管理', 'path': '/course', 'parent_id': None, 'icon': 'Reading', 'order': 4},
        {'name': '课程信息', 'path': '/course/list', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '班级课程', 'path': '/course/class', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '上课记录', 'path': '/record', 'parent_id': None, 'icon': 'Calendar', 'order': 5},
        {'name': '上课记录列表', 'path': '/record/list', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '学生上课', 'path': '/record/student', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '考勤记录', 'path': '/record/attendance', 'parent_id': None, 'icon': None, 'order': 3},
        {'name': '请假记录', 'path': '/leave', 'parent_id': None, 'icon': 'Postcard', 'order': 6},
        {'name': '请假记录列表', 'path': '/leave/list', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '请假审批', 'path': '/leave/approve', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '报表统计', 'path': '/report', 'parent_id': None, 'icon': 'DataAnalysis', 'order': 7},
        {'name': '学生统计', 'path': '/report/student', 'parent_id': None, 'icon': None, 'order': 1},
        {'name': '教师统计', 'path': '/report/teacher', 'parent_id': None, 'icon': None, 'order': 2},
        {'name': '班级统计', 'path': '/report/class', 'parent_id': None, 'icon': None, 'order': 3}
    ]
    
    for menu_data in menus:
        existing = Menu.query.filter_by(path=menu_data['path']).first()
        if not existing:
            menu = Menu(
                name=menu_data['name'],
                path=menu_data['path'],
                parent_id=menu_data['parent_id'],
                icon=menu_data['icon'],
                order=menu_data['order']
            )
            db.session.add(menu)
    
    db.session.commit()
    print('=' * 50)
    print('[SUCCESS] Initialization completed!')
    print('=' * 50)
    print('Admin account:')
    print('   Username: admin')
    print('   Password: admin123')
    print('=' * 50)
