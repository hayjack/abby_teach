from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import PaymentRecord, Student
from extensions import db
from datetime import date
from utils import parse_date

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    student_id = request.args.get('student_id')
    if student_id:
        payments = PaymentRecord.query.filter_by(student_id=student_id).all()
    else:
        payments = PaymentRecord.query.all()
    return jsonify([{
        'id': payment.id,
        'student_id': payment.student_id,
        'student_name': payment.student.name,
        'amount': float(payment.amount),
        'payment_date': payment.payment_date.isoformat(),
        'payment_type': payment.payment_type,
        'remark': payment.remark
    } for payment in payments])

@payment_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_payment(id):
    payment = PaymentRecord.query.get(id)
    if not payment:
        return jsonify({'message': '缴费记录不存在'}), 404
    return jsonify({
        'id': payment.id,
        'student_id': payment.student_id,
        'student_name': payment.student.name,
        'amount': float(payment.amount),
        'payment_date': payment.payment_date.isoformat(),
        'payment_type': payment.payment_type,
        'remark': payment.remark
    })

@payment_bp.route('/', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    student_id = data.get('student_id')
    amount = data.get('amount')
    payment_date = data.get('payment_date')
    payment_type = data.get('payment_type')
    remark = data.get('remark')
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    new_payment = PaymentRecord(
        student_id=student_id,
        amount=amount,
        payment_date=parse_date(payment_date),
        payment_type=payment_type,
        remark=remark
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'message': '缴费记录创建成功', 'id': new_payment.id}), 201

@payment_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_payment(id):
    payment = PaymentRecord.query.get(id)
    if not payment:
        return jsonify({'message': '缴费记录不存在'}), 404
    data = request.get_json()
    payment.amount = data.get('amount', payment.amount)
    if 'payment_date' in data:
        payment.payment_date = parse_date(data['payment_date'])
    payment.payment_type = data.get('payment_type', payment.payment_type)
    payment.remark = data.get('remark', payment.remark)
    db.session.commit()
    return jsonify({'message': '缴费记录更新成功'})

@payment_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_payment(id):
    payment = PaymentRecord.query.get(id)
    if not payment:
        return jsonify({'message': '缴费记录不存在'}), 404
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'message': '缴费记录删除成功'})
