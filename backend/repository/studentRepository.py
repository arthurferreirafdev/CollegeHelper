import logging
from backend.repository.database import get_db

logger = logging.getLogger(__name__)

class StudentRepository:

    @staticmethod
    def create(email, password_hash, first_name, last_name, grade_level, **kwargs):
        db = get_db()

        try:
            query = """
                INSERT INTO students (
                    email, password_hash, first_name, last_name, grade_level,
                    date_of_birth, phone_number, guardian_email
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            with db.cursor() as cur:
                cur.execute(query, (
                    email,
                    password_hash,
                    first_name,
                    last_name,
                    grade_level,
                    kwargs.get('date_of_birth'),
                    kwargs.get('phone_number'),
                    kwargs.get('guardian_email')
                ))
                student_id = cur.fetchone()["id"]

            db.commit()
            return student_id

        except Exception as e:
            db.rollback()
            logger.error(f'Error creating student: {e}')
            return None


    @staticmethod
    def find_by_email(email):
        db = get_db()

        query = """
            SELECT id, email, password_hash, first_name, last_name,
                   grade_level, is_active
            FROM students
            WHERE email = %s AND is_active = TRUE
        """

        with db.cursor() as cur:
            cur.execute(query, (email,))
            row = cur.fetchone()

        return row if row else None


    @staticmethod
    def find_by_id(student_id):
        db = get_db()

        query = """
            SELECT id, email, first_name, last_name, grade_level,
                   date_of_birth, phone_number, guardian_email,
                   is_active, created_at, updated_at
            FROM students
            WHERE id = %s
        """

        with db.cursor() as cur:
            cur.execute(query, (student_id,))
            row = cur.fetchone()

        return row if row else None


    @staticmethod
    def update(student_id, **kwargs):
        db = get_db()

        valid_fields = [
            'email', 'first_name', 'last_name', 'grade_level',
            'date_of_birth', 'phone_number', 'guardian_email', 'is_active'
        ]

        updates = []
        values = []

        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = %s")
                values.append(value)

        if not updates:
            return False

        # Atualiza timestamp no banco
        updates.append("updated_at = NOW()")

        values.append(student_id)

        query = f"""
            UPDATE students
            SET {', '.join(updates)}
            WHERE id = %s
        """

        try:
            with db.cursor() as cur:
                cur.execute(query, values)
                updated = cur.rowcount

            db.commit()
            return updated > 0

        except Exception as e:
            db.rollback()
            logger.error(f'Error updating student: {e}')
            return False