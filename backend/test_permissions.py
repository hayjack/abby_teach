from app import app
from models import User, Role, Class, ClassTeacher
from permissions import get_user_highest_priority_role, can_manage_class, can_manage_any_teacher

def test_permissions():
    with app.app_context():
        # Get a user with multiple roles
        user = User.query.get(1)  # admin user
        if not user:
            print("No user found with ID=1")
            return
        
        print(f"Testing user: {user.name}")
        print(f"User roles: {[r.name for r in user.roles]}")
        
        # Test get_user_highest_priority_role
        role_name, priority = get_user_highest_priority_role(user)
        print(f"Highest priority role: {role_name} (priority={priority})")
        
        # Test can_manage_any_teacher
        can_manage = can_manage_any_teacher(user)
        print(f"Can manage any teacher: {can_manage}")
        
        # Test can_manage_class with a sample class
        class_ = Class.query.first()
        if class_:
            can_manage = can_manage_class(user, class_)
            print(f"Can manage class '{class_.name}': {can_manage}")
        else:
            print("No classes found to test")

if __name__ == '__main__':
    test_permissions()
