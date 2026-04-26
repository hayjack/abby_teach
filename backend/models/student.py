from extensions import db
from datetime import datetime
from utils import now_local

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    english_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    parent_name = db.Column(db.String(50), nullable=False)
    parent_phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)

class StudentHoursHistory(db.Model):
    __tablename__ = 'student_hours_history'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    hours_added = db.Column(db.Numeric(5, 2), nullable=False)
    operator_id = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=now_local)
