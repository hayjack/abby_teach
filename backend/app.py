from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import timedelta
from extensions import db, migrate, jwt
from logging_config import setup_logging

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://teach_user:teach1234@localhost:5432/teach_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-in-production-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# 初始化扩展
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)

# 初始化日志系统
logger = setup_logging(app)
logger.info('=== 教学课程管理系统启动 ===')

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

@app.before_request
def log_request_info():
    logger.info(f'{request.method} {request.path}')

# 注册蓝图
from routes.auth import auth_bp
from routes.user import user_bp
from routes.role import role_bp
from routes.menu import menu_bp
from routes.student import student_bp
from routes.payment import payment_bp
from routes.course import course_bp
from routes.class_model import class_bp
from routes.class_record import class_record_bp
from routes.leave import leave_bp
from routes.report import report_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(role_bp, url_prefix='/api/roles')
app.register_blueprint(menu_bp, url_prefix='/api/menus')
app.register_blueprint(student_bp, url_prefix='/api/students')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(course_bp, url_prefix='/api/courses')
app.register_blueprint(class_bp, url_prefix='/api/classes')
app.register_blueprint(class_record_bp, url_prefix='/api/class_records')
app.register_blueprint(leave_bp, url_prefix='/api/leaves')
app.register_blueprint(report_bp, url_prefix='/api/reports')

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'status': 'ok', 'message': 'API is working'})

if __name__ == '__main__':
    logger.info('启动服务器: http://0.0.0.0:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
