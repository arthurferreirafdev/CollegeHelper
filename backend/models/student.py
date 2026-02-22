import logging
from backend.models.database import get_db

logger = logging.getLogger(__name__)


class StudentRepository:
    @staticmethod
    def create(email, password_hash, first_name, last_name, grade_level, **kwargs):
        db = get_db()
        try:
            db.execute(
                '''INSERT INTO students (email, password_hash, first_name, last_name, grade_level,
                   date_of_birth, phone_number, guardian_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (email, password_hash, first_name, last_name, grade_level,
                 kwargs.get('date_of_birth'), kwargs.get('phone_number'), kwargs.get('guardian_email'))
            )
            db.commit()
            return db.execute('SELECT last_insert_rowid()').fetchone()[0]
        except Exception as e:
            logger.error(f'Error creating student: {e}')
            return None

    @staticmethod
    def find_by_email(email):
        db = get_db()
        row = db.execute(
            'SELECT id, email, password_hash, first_name, last_name, grade_level, is_active FROM students WHERE email = ? AND is_active = 1',
            (email,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def find_by_id(student_id):
        db = get_db()
        row = db.execute(
            '''SELECT id, email, first_name, last_name, grade_level, 
               enrollment_number, course_id, date_of_birth,
               phone_number, guardian_email, is_active, created_at, updated_at
               FROM students WHERE id = ?''',
            (student_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def update(student_id, **kwargs):
        db = get_db()
        valid_fields = ['email', 'first_name', 'last_name', 'grade_level',
                        'enrollment_number', 'course_id',
                        'date_of_birth', 'phone_number', 'guardian_email', 'is_active']
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f'{field} = ?')
                values.append(value)
        if not updates:
            return False
        from datetime import datetime
        updates.append('updated_at = ?')
        values.append(datetime.now().isoformat())
        values.append(student_id)
        db.execute(f"UPDATE students SET {', '.join(updates)} WHERE id = ?", values)
        db.commit()
        return db.total_changes > 0
