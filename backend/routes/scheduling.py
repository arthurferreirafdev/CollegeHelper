import logging
from flask import Blueprint, request, jsonify
from backend.services.ai_service import AIService
from backend.services.scheduler_service import (
    SchedulerService, SchedulingPreferences, SchedulingStrategy,
    StudentAvailability, TimeSlot
)

logger = logging.getLogger(__name__)
scheduling_bp = Blueprint('scheduling', __name__)

STRATEGY_MAP = {
    'maximize_subjects': SchedulingStrategy.MAXIMIZE_SUBJECTS,
    'clear_dependencies': SchedulingStrategy.CLEAR_DEPENDENCIES,
    'balanced_difficulty': SchedulingStrategy.BALANCED_DIFFICULTY,
    'interest_based': SchedulingStrategy.INTEREST_BASED,
    'high_value_credits': SchedulingStrategy.HIGH_VALUE_CREDITS,
}

@scheduling_bp.route('/api/submit-preferences', methods=['POST'])
def submit_preferences():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        ai_service = AIService()
        if not ai_service.is_available():
            return jsonify({'error': 'AI service unavailable. OPENAI_API_KEY not configured.'}), 503

        result = ai_service.generate_schedule(data)
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        logger.error(f'Submit preferences error: {e}')
        return jsonify({'error': str(e)}), 500
