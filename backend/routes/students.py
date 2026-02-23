import logging
from flask import Blueprint, request, jsonify, g
from backend.middleware.auth_middleware import require_auth
from backend.models.studentRepository import StudentRepository
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)
students_bp = Blueprint('students', __name__)

@students_bp.route('/api/students/profile', methods=['GET'])
@require_auth
def get_profile():
    student = StudentRepository.find_by_id(g.current_student_id)
    if student:
        return jsonify({'success': True, 'student': student}), 200
    return jsonify({'error': 'Student not found'}), 404

@students_bp.route('/api/students/profile', methods=['PUT'])
@require_auth
def update_profile():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    success = StudentRepository.update(g.current_student_id, **data)
    if success:
        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
    return jsonify({'error': 'Failed to update profile'}), 400


@students_bp.route('/api/students/register', methods=['POST'])
def register_student():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['email', 'password', 'first_name', 'last_name', 'grade_level']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        password_hash = generate_password_hash(data['password'])

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

        print(student_id)

        if not student_id:
            return jsonify({'error': 'Failed to create student'}), 400

        return jsonify({
            'success': True,
            'student_id': student_id,
            'message': 'Student registered successfully'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
