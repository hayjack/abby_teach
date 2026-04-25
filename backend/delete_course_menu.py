from app import app, db
from models.menu import Menu

with app.app_context():
    # 删除课程统计菜单
    menu = Menu.query.filter_by(path='/report/course').first()
    if menu:
        db.session.delete(menu)
        db.session.commit()
        print('已删除课程统计菜单')
    else:
        print('课程统计菜单不存在')
    
    # 查看所有报表统计菜单
    print('\n当前报表统计菜单:')
    menus = Menu.query.filter(Menu.path.like('/report/%')).all()
    for menu in menus:
        print(f'{menu.name}: {menu.path}')