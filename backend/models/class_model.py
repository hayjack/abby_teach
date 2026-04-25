from extensions import db
from datetime import datetime
from utils import now_local, date

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)

class ClassStudent(db.Model):
    __tablename__ = 'class_students'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    join_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    class_ = db.relationship('Class', backref=db.backref('class_students', lazy=True), foreign_keys=[class_id], primaryjoin="ClassStudent.class_id == Class.id")
    student = db.relationship('Student', backref=db.backref('class_students', lazy=True), foreign_keys=[student_id], primaryjoin="ClassStudent.student_id == Student.id")

class ClassTeacher(db.Model):
    __tablename__ = 'class_teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    class_ = db.relationship('Class', backref=db.backref('class_teachers', lazy=True), foreign_keys=[class_id], primaryjoin="ClassTeacher.class_id == Class.id")
    teacher = db.relationship('User', backref=db.backref('class_teachers', lazy=True), foreign_keys=[teacher_id], primaryjoin="ClassTeacher.teacher_id == User.id")

class ClassCourse(db.Model):
    __tablename__ = 'class_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)
    
    class_ = db.relationship('Class', backref=db.backref('class_courses', lazy=True), foreign_keys=[class_id], primaryjoin="ClassCourse.class_id == Class.id")
    course = db.relationship('Course', backref=db.backref('class_courses', lazy=True), foreign_keys=[course_id], primaryjoin="ClassCourse.course_id == Course.id")
