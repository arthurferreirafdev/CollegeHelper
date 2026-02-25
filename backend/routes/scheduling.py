# import logging
# from datetime import time
# from flask import Blueprint, request, jsonify, g
# from backend.middleware.auth_middleware import require_auth
# from backend.services.scheduler_service import (
#     SchedulerService, SchedulingPreferences, SchedulingStrategy,
#     StudentAvailability, TimeSlot
# )

# logger = logging.getLogger(__name__)
# scheduling_bp = Blueprint('scheduling', __name__)

# STRATEGY_MAP = {
#     'maximize_subjects': SchedulingStrategy.MAXIMIZE_SUBJECTS,
#     'clear_dependencies': SchedulingStrategy.CLEAR_DEPENDENCIES,
#     'balanced_difficulty': SchedulingStrategy.BALANCED_DIFFICULTY,
#     'interest_based': SchedulingStrategy.INTEREST_BASED,
#     'high_value_credits': SchedulingStrategy.HIGH_VALUE_CREDITS,
# }

# @scheduling_bp.route('/api/submit-preferences', methods=['POST'])
# def submit_preferences():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'No data provided'}), 400

#     try:
#         weekly = []
#         for day_data in data.get('weeklySchedule', []):
#             slots = []
#             if day_data.get('available', False):
#                 for sl in day_data.get('timeSlots', []):
#                     slots.append(TimeSlot(
#                         day=day_data['day'],
#                         start_time=time.fromisoformat(sl['start']),
#                         end_time=time.fromisoformat(sl['end'])
#                     ))
#             weekly.append(StudentAvailability(
#                 day=day_data['day'],
#                 available=day_data.get('available', False),
#                 time_slots=slots
#             ))

#         prefs = SchedulingPreferences(
#             student_id=0,
#             subject_count=data.get('subjectCount', 5),
#             strategy=STRATEGY_MAP.get(data.get('preferenceStrategy', ''), SchedulingStrategy.INTEREST_BASED),
#             prioritize_dependencies=data.get('prioritizeDependencies', False),
#             include_saturday=data.get('includeSaturday', False),
#             weekly_availability=weekly,
#             additional_notes=data.get('additionalNotes', ''),
#             uploaded_subjects=data.get('uploadedSubjects', [])
#         )

#         scheduler = SchedulerService()
#         result = scheduler.create_optimal_schedule(prefs)
#         return jsonify(result), 200 if result.get('success') else 400
#     except Exception as e:
#         logger.error(f'Submit preferences error: {e}')
#         return jsonify({'error': str(e)}), 500
