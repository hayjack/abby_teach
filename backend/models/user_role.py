from extensions import db
from datetime import datetime
from utils import now_local

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)
