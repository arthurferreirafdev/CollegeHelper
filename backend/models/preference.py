import logging
from backend.models.database import get_db

logger = logging.getLogger(__name__)


class PreferenceRepository:
    @staticmethod
    def get_by_student(student_id):
        db = get_db()
        rows = db.execute(
            '''SELECT sp.id, sp.student_id, sp.subject_id, s.name as subject_name,
               s.code as subject_code, s.category, s.difficulty_level,
               sp.interest_level, sp.priority, sp.notes, sp.status,
               sp.created_at, sp.updated_at
               FROM student_preferences sp
               JOIN subjects s ON sp.subject_id = s.id
               WHERE sp.student_id = ? AND s.is_active = 1
               ORDER BY sp.priority ASC, sp.interest_level DESC''',
            (student_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def add(student_id, subject_id, interest_level, priority=None, notes=None, status='interested'):
        db = get_db()
        try:
            db.execute(
                '''INSERT OR REPLACE INTO student_preferences
                   (student_id, subject_id, interest_level, priority, notes, status)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (student_id, subject_id, interest_level, priority, notes, status)
            )
            db.commit()
            return db.execute('SELECT last_insert_rowid()').fetchone()[0]
        except Exception as e:
            logger.error(f'Error adding preference: {e}')
            return None

    @staticmethod
    def remove(preference_id, student_id):
        db = get_db()
        # Get the subject_id from the preference first
        pref = db.execute(
            'SELECT subject_id FROM student_preferences WHERE id = ? AND student_id = ?',
            (preference_id, student_id)
        ).fetchone()
        if not pref:
            return False
        db.execute(
            'DELETE FROM student_preferences WHERE id = ? AND student_id = ?',
            (preference_id, student_id)
        )
        db.commit()
        return True
