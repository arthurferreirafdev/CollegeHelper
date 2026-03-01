import logging
from flask import Blueprint, request, jsonify
from backend.repository.subjectRepository import SubjectRepository

logger = logging.getLogger(__name__)
subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/api/subjects', methods=['GET'])
def get_subjects():
    category = request.args.get('category')
    if category:
        subjects = SubjectRepository.get_by_category(category)
    else:
        subjects = SubjectRepository.get_all()
    return jsonify({'success': True, 'subjects': subjects}), 200

@subjects_bp.route('/api/subjects/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = SubjectRepository.find_by_id(subject_id)
    if subject:
        return jsonify({'success': True, 'subject': subject}), 200
    return jsonify({'error': 'Subject not found'}), 404

@subjects_bp.route('/api/subjects/categories', methods=['GET'])
def get_categories():
    categories = SubjectRepository.get_categories()
    return jsonify({'success': True, 'categories': categories}), 200
