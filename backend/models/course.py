from extensions import db
from datetime import datetime
from utils import now_local

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    total_hours = db.Column(db.Numeric(5, 2), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)

class StudentCourse(db.Model):
    __tablename__ = 'student_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    total_hours = db.Column(db.Numeric(5, 2), nullable=False)
    remaining_hours = db.Column(db.Numeric(5, 2), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    student = db.relationship('Student', backref=db.backref('student_courses', lazy=True), foreign_keys=[student_id], primaryjoin="StudentCourse.student_id == Student.id")
    course = db.relationship('Course', backref=db.backref('student_courses', lazy=True), foreign_keys=[course_id], primaryjoin="StudentCourse.course_id == Course.id")
