from extensions import db
from datetime import datetime
from utils import now_local

class ClassRecord(db.Model):
    __tablename__ = 'class_records'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)
    class_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours = db.Column(db.Numeric(4, 2), nullable=False)
    content = db.Column(db.String(500))
    is_makeup = db.Column(db.Boolean, default=False, nullable=False)  # 是否为补课
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    class_ = db.relationship('Class', backref=db.backref('class_records', lazy=True), foreign_keys=[class_id], primaryjoin="ClassRecord.class_id == Class.id")
    course = db.relationship('Course', backref=db.backref('class_records', lazy=True), foreign_keys=[course_id], primaryjoin="ClassRecord.course_id == Course.id")
    teacher = db.relationship('User', backref=db.backref('class_records', lazy=True), foreign_keys=[teacher_id], primaryjoin="ClassRecord.teacher_id == User.id")

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    class_record_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 出勤/请假/旷课
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    class_record = db.relationship('ClassRecord', backref=db.backref('attendance_records', lazy=True), foreign_keys=[class_record_id], primaryjoin="AttendanceRecord.class_record_id == ClassRecord.id")
    student = db.relationship('Student', backref=db.backref('attendance_records', lazy=True), foreign_keys=[student_id], primaryjoin="AttendanceRecord.student_id == Student.id")
