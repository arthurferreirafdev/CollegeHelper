import logging
from backend.models.database import get_db

logger = logging.getLogger(__name__)


class SubjectRepository:
    @staticmethod
    def get_all(active_only=True):
        db = get_db()
        query = '''SELECT id, name, code, description, category,course_id, difficulty_level,
                   credits, prerequisites, teacher_name, max_students, semester,
                   schedule, is_active, created_at FROM subjects'''
        if active_only:
            query += ' WHERE is_active = 1'
        query += ' ORDER BY category, name'
        rows = db.execute(query).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def find_by_id(subject_id):
        db = get_db()
        row = db.execute(
            '''SELECT id, name, code, description, category, difficulty_level,
               credits, prerequisites, teacher_name, max_students, semester,
               schedule, is_active, created_at FROM subjects WHERE id = ?''',
            (subject_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_categories():
        db = get_db()
        rows = db.execute(
            'SELECT DISTINCT category FROM subjects WHERE is_active = 1 ORDER BY category'
        ).fetchall()
        return [row['category'] for row in rows]

    @staticmethod
    def get_by_category(category, active_only=True):
        db = get_db()
        query = '''SELECT id, name, code, description, category, difficulty_level,
                   credits, prerequisites, teacher_name, max_students, semester,
                   schedule, is_active, created_at FROM subjects WHERE category = ?'''
        if active_only:
            query += ' AND is_active = 1'
        query += ' ORDER BY name'
        rows = db.execute(query, (category,)).fetchall()
        return [dict(row) for row in rows]
