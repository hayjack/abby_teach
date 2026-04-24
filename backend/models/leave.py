from extensions import db
from datetime import datetime, date
from utils import now_local

class LeaveRecord(db.Model):
    __tablename__ = 'leave_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='待审批')
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    student = db.relationship('Student', backref=db.backref('leave_records', lazy=True))
    course = db.relationship('Course', backref=db.backref('leave_records', lazy=True))
