import logging
from flask import Blueprint, request, jsonify
from backend.repository.studentRepository import StudentRepository
from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    student = StudentRepository.find_by_email(data['email'])
    print(student)
    if not student or not AuthService.verify_password(data['password'], student['password_hash']):
        return jsonify({
        'success': False,
        'message': 'Invalid email or password',
        'token': token,
        'student': {}
    }), 401

    token = AuthService.generate_token(student['id'])
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'student': {
            'id': student['id'],
            'email': student['email'],
            'first_name': student['first_name'],
            'last_name': student['last_name'],
            'grade_level': student['grade_level']
        }
    }), 200

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
