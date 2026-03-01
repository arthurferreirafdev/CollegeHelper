from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from flask import current_app


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)

    @staticmethod
    def generate_token(student_id: int) -> str:
        payload = {
            'student_id': student_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload['student_id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
