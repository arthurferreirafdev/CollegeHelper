import logging
from flask import Blueprint, request, jsonify, g
from backend.middleware.auth_middleware import require_auth
from backend.models.student import StudentRepository

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
