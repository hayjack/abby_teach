from extensions import db
from datetime import datetime
from utils import now_local
from models.user_role import UserRole
from models.menu import RoleMenu

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    priority = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    # 多对多关系：一个角色可以有多个用户
    users = db.relationship('User', 
                           secondary='user_roles', 
                           primaryjoin="Role.id == UserRole.role_id",
                           secondaryjoin="User.id == UserRole.user_id")
    
    # 多对多关系：一个角色可以有多个菜单
    menus = db.relationship('Menu', 
                           secondary='role_menus', 
                           primaryjoin="Role.id == RoleMenu.role_id",
                           secondaryjoin="Menu.id == RoleMenu.menu_id")
