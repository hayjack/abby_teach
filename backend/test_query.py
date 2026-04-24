from app import app
from models import User, Role, UserRole

with app.app_context():
    u = User.query.first()
    print('User:', u.name if u else 'None')
    r = Role.query.first()
    print('Role:', r.name if r else 'None')
    print('All queries OK')
