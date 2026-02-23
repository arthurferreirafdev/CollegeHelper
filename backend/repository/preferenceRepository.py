import logging
from backend.repository.database import get_db

logger = logging.getLogger(__name__)


class PreferenceRepository:

    @staticmethod
    def get_by_student(student_id):
        db = get_db()

        query = """
            SELECT sp.id, sp.student_id, sp.subject_id, s.name as subject_name,
                   s.code as subject_code, s.category, s.difficulty_level,
                   sp.interest_level, sp.priority, sp.notes, sp.status,
                   sp.created_at, sp.updated_at
            FROM student_preferences sp
            JOIN subjects s ON sp.subject_id = s.id
            WHERE sp.student_id = %s AND s.is_active = TRUE
            ORDER BY sp.priority ASC, sp.interest_level DESC
        """

        with db.cursor() as cur:
            cur.execute(query, (student_id,))
            rows = cur.fetchall()

        return rows  # já são dicts se você configurou dict_row


    @staticmethod
    def add(student_id, subject_id, interest_level, priority=None, notes=None, status='interested'):
        db = get_db()

        try:
            query = """
                INSERT INTO student_preferences
                (student_id, subject_id, interest_level, priority, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id, subject_id)
                DO UPDATE SET
                    interest_level = EXCLUDED.interest_level,
                    priority = EXCLUDED.priority,
                    notes = EXCLUDED.notes,
                    status = EXCLUDED.status,
                    updated_at = NOW()
                RETURNING id
            """

            with db.cursor() as cur:
                cur.execute(query, (
                    student_id, subject_id, interest_level,
                    priority, notes, status
                ))
                preference_id = cur.fetchone()["id"]

            db.commit()
            return preference_id

        except Exception as e:
            db.rollback()
            logger.error(f'Error adding preference: {e}')
            return None


    @staticmethod
    def remove(preference_id, student_id):
        db = get_db()

        try:
            with db.cursor() as cur:
                # Verifica se existe
                cur.execute(
                    """
                    SELECT subject_id
                    FROM student_preferences
                    WHERE id = %s AND student_id = %s
                    """,
                    (preference_id, student_id)
                )
                pref = cur.fetchone()

                if not pref:
                    return False

                # Remove
                cur.execute(
                    """
                    DELETE FROM student_preferences
                    WHERE id = %s AND student_id = %s
                    """,
                    (preference_id, student_id)
                )

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(f'Error removing preference: {e}')
            return False