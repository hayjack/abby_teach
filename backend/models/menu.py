from extensions import db
from datetime import datetime
from utils import now_local

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer)
    icon = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    parent = db.relationship('Menu', 
                           remote_side=[id], 
                           backref=db.backref('children', lazy=True), 
                           foreign_keys=[parent_id],
                           primaryjoin="Menu.parent_id == Menu.id")

class RoleMenu(db.Model):
    __tablename__ = 'role_menus'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)
    menu_id = db.Column(db.Integer, nullable=False)
