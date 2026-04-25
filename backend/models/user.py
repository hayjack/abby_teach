from extensions import db
from datetime import datetime
from utils import now_local
from models.user_role import UserRole

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    english_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    # 多对多关系：一个用户可以有多个角色
    roles = db.relationship('Role', 
                           secondary='user_roles', 
                           primaryjoin="User.id == UserRole.user_id",
                           secondaryjoin="Role.id == UserRole.role_id")
