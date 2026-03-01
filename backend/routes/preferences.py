import logging
from flask import Blueprint, request, jsonify, g
from backend.middleware.auth_middleware import require_auth
from backend.repository.preferenceRepository import PreferenceRepository

logger = logging.getLogger(__name__)
preferences_bp = Blueprint('preferences', __name__)

@preferences_bp.route('/api/preferences', methods=['GET'])
@require_auth
def get_preferences():
    preferences = PreferenceRepository.get_by_student(g.current_student_id)
    return jsonify({'success': True, 'preferences': preferences}), 200

@preferences_bp.route('/api/preferences', methods=['POST'])
@require_auth
def add_preference():
    data = request.get_json()
    if not data or not data.get('subject_id') or not data.get('interest_level'):
        return jsonify({'error': 'subject_id and interest_level are required'}), 400

    if not (1 <= data['interest_level'] <= 5):
        return jsonify({'error': 'Interest level must be between 1 and 5'}), 400

    preference_id = PreferenceRepository.add(
        student_id=g.current_student_id,
        subject_id=data['subject_id'],
        interest_level=data['interest_level'],
        priority=data.get('priority'),
        notes=data.get('notes'),
        status=data.get('status', 'interested')
    )

    if preference_id:
        return jsonify({'success': True, 'message': 'Preference added successfully', 'preference_id': preference_id}), 201
    return jsonify({'error': 'Failed to add preference'}), 400

@preferences_bp.route('/api/preferences/<int:preference_id>', methods=['DELETE'])
@require_auth
def remove_preference(preference_id):
    success = PreferenceRepository.remove(preference_id, g.current_student_id)
    if success:
        return jsonify({'success': True, 'message': 'Preference removed successfully'}), 200
    return jsonify({'error': 'Preference not found or access denied'}), 404
