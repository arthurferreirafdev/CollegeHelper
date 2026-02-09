from functools import wraps
from flask import request, jsonify, g
from backend.services.auth_service import AuthService


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401

        token = auth_header.split(' ')[1]
        student_id = AuthService.verify_token(token)

        if not student_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        g.current_student_id = student_id
        return f(*args, **kwargs)
    return decorated
