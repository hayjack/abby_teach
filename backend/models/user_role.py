from extensions import db
from datetime import datetime
from utils import now_local

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)
    
    user = db.relationship('User', backref=db.backref('user_roles', lazy=True))
    role = db.relationship('Role', backref=db.backref('user_roles', lazy=True))
