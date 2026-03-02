from flask import Blueprint, request, jsonify, g
from backend.models.grade_horaria import GradeHorariaRepository
from backend.middleware.auth_middleware import require_auth

grade_horaria_bp = Blueprint('grade_horaria', __name__)

@grade_horaria_bp.route('/grade-horaria', methods=['POST'])
@require_auth
def create_grade():
    data = request.get_json()
    student_id = g.current_student_id
    
    existing = GradeHorariaRepository.find_by_student(student_id)
    if existing:
        return jsonify({
            'success': False,
            'message': 'Student already has a grade horaria'
        }), 409
    
    grade_id = GradeHorariaRepository.create(
        student_id=student_id,
        semester=data.get('semester'),
        status=data.get('status', 'draft')
    )
    
    return jsonify({
        'success': True,
        'message': 'Grade horaria created successfully',
        'grade_id': grade_id
    }), 201

@grade_horaria_bp.route('/grade-horaria', methods=['GET'])
@require_auth
def get_grade():
    student_id = g.current_student_id
    grade = GradeHorariaRepository.find_by_student(student_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    subjects = GradeHorariaRepository.get_subjects(grade['id'])
    grade['subjects'] = subjects
    
    return jsonify({
        'success': True,
        'grade': grade
    }), 200

@grade_horaria_bp.route('/grade-horaria/<int:grade_id>', methods=['GET'])
@require_auth
def get_grade_by_id(grade_id):
    grade = GradeHorariaRepository.find_by_id(grade_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    if grade['student_id'] != g.current_student_id:
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 403
    
    subjects = GradeHorariaRepository.get_subjects(grade_id)
    grade['subjects'] = subjects
    
    return jsonify({
        'success': True,
        'grade': grade
    }), 200

@grade_horaria_bp.route('/grade-horaria/<int:grade_id>', methods=['PUT'])
@require_auth
def update_grade(grade_id):
    grade = GradeHorariaRepository.find_by_id(grade_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    if grade['student_id'] != g.current_student_id:
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 403
    
    data = request.get_json()
    success = GradeHorariaRepository.update(grade_id, **data)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Grade horaria updated successfully'
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'No valid fields to update'
    }), 400

@grade_horaria_bp.route('/grade-horaria/<int:grade_id>', methods=['DELETE'])
@require_auth
def delete_grade(grade_id):
    grade = GradeHorariaRepository.find_by_id(grade_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    if grade['student_id'] != g.current_student_id:
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 403
    
    GradeHorariaRepository.delete(grade_id)
    
    return jsonify({
        'success': True,
        'message': 'Grade horaria deleted successfully'
    }), 200

@grade_horaria_bp.route('/grade-horaria/<int:grade_id>/subjects', methods=['POST'])
@require_auth
def add_subject_to_grade(grade_id):
    grade = GradeHorariaRepository.find_by_id(grade_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    if grade['student_id'] != g.current_student_id:
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 403
    
    data = request.get_json()
    subject_id = data.get('subject_id')
    
    if not subject_id:
        return jsonify({
            'success': False,
            'message': 'subject_id is required'
        }), 400
    
    result = GradeHorariaRepository.add_subject(grade_id, subject_id)
    
    if result:
        return jsonify({
            'success': True,
            'message': 'Subject added to grade horaria'
        }), 201
    
    return jsonify({
        'success': False,
        'message': 'Subject already in grade or does not exist'
    }), 409

@grade_horaria_bp.route('/grade-horaria/<int:grade_id>/subjects/<int:subject_id>', methods=['DELETE'])
@require_auth
def remove_subject_from_grade(grade_id, subject_id):
    grade = GradeHorariaRepository.find_by_id(grade_id)
    
    if not grade:
        return jsonify({
            'success': False,
            'message': 'Grade horaria not found'
        }), 404
    
    if grade['student_id'] != g.current_student_id:
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 403
    
    success = GradeHorariaRepository.remove_subject(grade_id, subject_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Subject removed from grade horaria'
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'Subject not found in grade'
    }), 404
