from .auth import auth_bp
from .user import user_bp
from .role import role_bp
from .menu import menu_bp
from .student import student_bp
from .payment import payment_bp
from .course import course_bp
from .class_model import class_bp
from .class_record import class_record_bp
from .leave import leave_bp
from .report import report_bp

__all__ = [
    'auth_bp', 'user_bp', 'role_bp', 'menu_bp', 
    'student_bp', 'payment_bp', 'course_bp', 'class_bp',
    'class_record_bp', 'leave_bp', 'report_bp'
]
