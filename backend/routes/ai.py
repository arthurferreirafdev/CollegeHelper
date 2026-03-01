import logging
from flask import Blueprint, request, jsonify, g
from backend.middleware.auth_middleware import require_auth
from backend.services.ai_service import AIService

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/ai/recommendations', methods=['POST'])
# @require_auth
def get_recommendations():
    ai = AIService()
    if not ai.is_available():
        return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503

    print("RECOMENDATIOOOOOOOOOONSNS", request.get_json())
    data = request.get_json() or {}
    result = ai.get_subject_recommendations(
        student_id="g.current_student_id",
        additional_context=data.get('additional_context', '')
    )

    print(result)
    return jsonify(result), 200

@ai_bp.route('/api/ai/subject-analysis', methods=['POST'])
@require_auth
def analyze_subject():
    ai = AIService()
    if not ai.is_available():
        return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503

    data = request.get_json()
    if not data or not data.get('subject_name'):
        return jsonify({'error': 'subject_name is required'}), 400

    result = ai.analyze_subject_fit(
        student_id=g.current_student_id,
        subject_name=data['subject_name']
    )
    return jsonify(result), 200

@ai_bp.route('/api/ai/career-advice', methods=['POST'])
@require_auth
def get_career_advice():
    ai = AIService()
    if not ai.is_available():
        return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503

    data = request.get_json()
    if not data or not data.get('career_interest'):
        return jsonify({'error': 'career_interest is required'}), 400

    result = ai.get_career_advice(
        student_id=g.current_student_id,
        career_interest=data['career_interest']
    )
    return jsonify(result), 200

@ai_bp.route('/api/ai/study-plan', methods=['POST'])
@require_auth
def generate_study_plan():
    ai = AIService()
    if not ai.is_available():
        return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503

    data = request.get_json()
    if not data or not data.get('selected_subjects'):
        return jsonify({'error': 'selected_subjects is required'}), 400

    result = ai.generate_study_plan(
        student_id=g.current_student_id,
        selected_subjects=data['selected_subjects'],
        semester=data.get('semester', 'Current Semester')
    )
    return jsonify(result), 200
