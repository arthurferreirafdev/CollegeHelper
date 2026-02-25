import logging
from flask import Blueprint, request, jsonify
from backend.repository.studentRepository import StudentRepository
from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['email', 'password', 'first_name', 'last_name', 'grade_level']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if not (9 <= data['grade_level'] <= 12):
        return jsonify({'error': 'Grade level must be between 9 and 12'}), 400

    password_hash = AuthService.hash_password(data['password'])
    student_id = StudentRepository.create(
        email=data['email'],
        password_hash=password_hash,
        first_name=data['first_name'],
        last_name=data['last_name'],
        grade_level=data['grade_level'],
        date_of_birth=data.get('date_of_birth'),
        phone_number=data.get('phone_number'),
        guardian_email=data.get('guardian_email')
    )

    if student_id:
        return jsonify({'success': True, 'message': 'Registration successful', 'student_id': student_id}), 201
    return jsonify({'error': 'Registration failed - email may already exist'}), 400

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    student = StudentRepository.find_by_email(data['email'])
    if not student or not AuthService.verify_password(data['password'], student['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

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
