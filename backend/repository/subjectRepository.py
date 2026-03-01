import logging
from backend.repository.database import get_db

logger = logging.getLogger(__name__)


class SubjectRepository:

    @staticmethod
    def get_all(active_only=True):
        db = get_db()

        query = """
            SELECT id, name, code, description, category, difficulty_level,
                   credits, prerequisites, teacher_name, max_students, semester,
                   schedule, is_active, created_at
            FROM subjects
        """

        if active_only:
            query += " WHERE is_active = TRUE"

        query += " ORDER BY category, name"

        with db.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        return rows


    @staticmethod
    def find_by_id(subject_id):
        db = get_db()

        query = """
            SELECT id, name, code, description, category, difficulty_level,
                   credits, prerequisites, teacher_name, max_students, semester,
                   schedule, is_active, created_at
            FROM subjects
            WHERE id = %s
        """

        with db.cursor() as cur:
            cur.execute(query, (subject_id,))
            row = cur.fetchone()

        return row if row else None


    @staticmethod
    def get_categories():
        db = get_db()

        query = """
            SELECT DISTINCT category
            FROM subjects
            WHERE is_active = TRUE
            ORDER BY category
        """

        with db.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        return [row["category"] for row in rows]


    @staticmethod
    def get_by_category(category, active_only=True):
        db = get_db()

        query = """
            SELECT id, name, code, description, category, difficulty_level,
                   credits, prerequisites, teacher_name, max_students, semester,
                   schedule, is_active, created_at
            FROM subjects
            WHERE category = %s
        """

        params = [category]

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY name"

        with db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        return rows