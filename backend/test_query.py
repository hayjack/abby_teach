from app import app
from models import User, Role, UserRole, Menu

with app.app_context():
    u = User.query.first()
    print('User:', u.name if u else 'None')
    r = Role.query.first()
    print('Role:', r.name if r else 'None')
    
    # 测试查询菜单
    print('\nMenus:')
    menus = Menu.query.filter(Menu.path.like('/report/%')).all()
    for menu in menus:
        print(f'{menu.name}: {menu.path}')
    
    print('\nAll queries OK')
