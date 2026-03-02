from backend.repository.database import get_db

class GradeHorariaRepository:
    @staticmethod
    def create(student_id, semester=None, status='draft'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO grade_horaria (student_id, semester, status) VALUES (%s, %s, %s) RETURNING id",
            (student_id, semester, status)
        )
        grade_id = cursor.fetchone()[0]
        db.commit()
        return grade_id

    @staticmethod
    def find_by_id(grade_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT g.id, g.student_id, g.semester, g.status, g.created_at, g.updated_at
               FROM grade_horaria g WHERE g.id = %s""",
            (grade_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            'id': row[0],
            'student_id': row[1],
            'semester': row[2],
            'status': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        }

    @staticmethod
    def find_by_student(student_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT g.id, g.student_id, g.semester, g.status, g.created_at, g.updated_at
               FROM grade_horaria g WHERE g.student_id = %s""",
            (student_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            'id': row[0],
            'student_id': row[1],
            'semester': row[2],
            'status': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        }

    @staticmethod
    def update(grade_id, **kwargs):
        allowed_fields = ['semester', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        set_clause += ", updated_at = NOW()"
        values = list(updates.values()) + [grade_id]
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"UPDATE grade_horaria SET {set_clause} WHERE id = %s", values)
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete(grade_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM grade_horaria WHERE id = %s", (grade_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def add_subject(grade_id, subject_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO grade_horaria_subjects (grade_id, subject_id) VALUES (%s, %s) RETURNING id",
                (grade_id, subject_id)
            )
            result_id = cursor.fetchone()[0]
            db.commit()
            return result_id
        except Exception:
            db.rollback()
            return None

    @staticmethod
    def remove_subject(grade_id, subject_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM grade_horaria_subjects WHERE grade_id = %s AND subject_id = %s",
            (grade_id, subject_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_subjects(grade_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT s.id, s.name, s.code, s.category, s.difficulty_level, 
                      s.credits, s.schedule, s.teacher_name
               FROM grade_horaria_subjects gs
               JOIN subjects s ON gs.subject_id = s.id
               WHERE gs.grade_id = %s
               ORDER BY s.name""",
            (grade_id,)
        )
        subjects = []
        for row in cursor.fetchall():
            subjects.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'category': row[3],
                'difficulty_level': row[4],
                'credits': row[5],
                'schedule': row[6],
                'teacher_name': row[7]
            })
        return subjects
