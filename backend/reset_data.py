from app import app, db
from models.user import User
from models.role import Role
from models.menu import Menu
from models.user_role import UserRole
from models.student import Student
from models.class_model import Class
from models.course import Course
from models.class_record import ClassRecord, AttendanceRecord
from models.leave import LeaveRecord
from models.payment import PaymentRecord
from models.class_model import ClassStudent, ClassTeacher, ClassCourse
from models.course import StudentCourse

with app.app_context():
    print('=' * 50)
    print('[INFO] Starting data reset...')
    print('=' * 50)
    
    # 保留的表：user, role, menu, user_role
    # 需要重置的表：student, class, course, class_record, leave, payment
    
    # 1. 删除需要重置的表数据
    print('[INFO] Deleting data from tables to reset...')
    
    # 先删除关联表数据
    db.session.query(AttendanceRecord).delete()
    db.session.query(ClassRecord).delete()
    db.session.query(LeaveRecord).delete()
    db.session.query(PaymentRecord).delete()
    db.session.query(ClassStudent).delete()
    db.session.query(ClassTeacher).delete()
    db.session.query(ClassCourse).delete()
    db.session.query(StudentCourse).delete()
    
    # 然后删除主表数据
    db.session.query(Student).delete()
    db.session.query(Class).delete()
    db.session.query(Course).delete()
    
    db.session.commit()
    print('[OK] Data deleted successfully')
    
    # 2. 重置表的ID自增值
    print('[INFO] Resetting table auto-increment values...')
    
    # 获取数据库连接
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    
    # 重置各个表的自增值
    tables_to_reset = [
        'students',
        'classes',
        'courses',
        'class_records',
        'attendance_records',
        'leave_records',
        'payment_records',
        'class_students',
        'class_teachers',
        'class_courses',
        'student_courses'
    ]
    
    for table in tables_to_reset:
        try:
            # PostgreSQL 语法：ALTER SEQUENCE table_name_id_seq RESTART WITH 1
            cursor.execute(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
            print(f'[OK] Reset auto-increment for table: {table}')
        except Exception as e:
            print(f'[ERROR] Failed to reset auto-increment for table {table}: {e}')
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print('=' * 50)
    print('[SUCCESS] Data reset completed!')
    print('[INFO] Kept data: users, roles, menus, user_roles')
    print('[INFO] Reset data: students, classes, courses, class_records, leaves, payments')
    print('[INFO] Reset auto-increment values for all reset tables')
    print('=' * 50)
