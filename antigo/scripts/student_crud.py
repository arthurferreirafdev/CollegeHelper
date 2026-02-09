import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

class StudentCRUD:
    """
    Comprehensive CRUD operations for the student subject selection system.
    Handles all database interactions with proper error handling and security considerations.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize CRUD operations with configurable database path.
        
        Args:
            db_path (str, optional): Custom database path. Uses environment variable or default.
        """
        # Use environment variable or default path for database location
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'data/student_subjects.db')
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}. Run database_setup.py first.")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection with proper configuration.
        
        Returns:
            sqlite3.Connection: Configured database connection
        """
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==========================================
    # STUDENT MANAGEMENT OPERATIONS
    # ==========================================
    
    def create_student(self, email: str, password: str, first_name: str, 
                      last_name: str, grade_level: int, **kwargs) -> int:
        """
        Create a new student account with secure password handling.
        
        Args:
            email (str): Student's email address (must be unique)
            password (str): Plain text password (will be hashed)
            first_name (str): Student's first name
            last_name (str): Student's last name
            grade_level (int): Grade level (9-12)
            **kwargs: Optional fields (date_of_birth, phone_number, guardian_email)
        
        Returns:
            int: Student ID if successful, -1 if failed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Hash the password for security
            password_hash = self._hash_password(password)
            
            # Prepare optional fields
            date_of_birth = kwargs.get('date_of_birth')
            phone_number = kwargs.get('phone_number')
            guardian_email = kwargs.get('guardian_email')
            
            # Insert new student record
            cursor.execute('''
                INSERT INTO students (email, password_hash, first_name, last_name, grade_level,
                                    date_of_birth, phone_number, guardian_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, grade_level,
                  date_of_birth, phone_number, guardian_email))
            
            student_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Student created successfully with ID: {student_id}")
            return student_id
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Error creating student (likely duplicate email): {e}")
            return -1
        except Exception as e:
            print(f"❌ Unexpected error creating student: {e}")
            return -1
        finally:
            conn.close()
    
    def authenticate_student(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a student login attempt.
        
        Args:
            email (str): Student's email address
            password (str): Plain text password
        
        Returns:
            Optional[Dict]: Student data if authentication successful, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get student record with password hash
            cursor.execute('''
                SELECT id, email, password_hash, first_name, last_name, grade_level, is_active
                FROM students WHERE email = ? AND is_active = 1
            ''', (email,))
            
            row = cursor.fetchone()
            
            if row and self._verify_password(password, row[2]):
                # Password matches, return student data (excluding password hash)
                return {
                    'id': row[0],
                    'email': row[1],
                    'first_name': row[3],
                    'last_name': row[4],
                    'grade_level': row[5],
                    'is_active': row[6]
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return None
        finally:
            conn.close()
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a student's information by ID.
        
        Args:
            student_id (int): Student's unique ID
        
        Returns:
            Optional[Dict]: Student data if found, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, first_name, last_name, grade_level, date_of_birth,
                       phone_number, guardian_email, is_active, created_at, updated_at
                FROM students WHERE id = ?
            ''', (student_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'grade_level': row[4],
                    'date_of_birth': row[5],
                    'phone_number': row[6],
                    'guardian_email': row[7],
                    'is_active': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving student: {e}")
            return None
        finally:
            conn.close()
    
    def get_student_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a student's information by email address.
        
        Args:
            email (str): Student's email address
        
        Returns:
            Optional[Dict]: Student data if found, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, first_name, last_name, grade_level, date_of_birth,
                       phone_number, guardian_email, is_active, created_at, updated_at
                FROM students WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'grade_level': row[4],
                    'date_of_birth': row[5],
                    'phone_number': row[6],
                    'guardian_email': row[7],
                    'is_active': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving student by email: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_students(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve all students from the database.
        
        Args:
            active_only (bool): If True, only return active students
        
        Returns:
            List[Dict]: List of student records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build query based on active_only parameter
            query = '''
                SELECT id, email, first_name, last_name, grade_level, is_active, created_at
                FROM students
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY last_name, first_name'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'email': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'grade_level': row[4],
                    'is_active': row[5],
                    'created_at': row[6]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ Error retrieving students: {e}")
            return []
        finally:
            conn.close()
    
    def update_student(self, student_id: int, **kwargs) -> bool:
        """
        Update student information with flexible field updates.
        
        Args:
            student_id (int): Student's unique ID
            **kwargs: Fields to update (email, first_name, last_name, etc.)
        
        Returns:
            bool: True if update successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Define valid fields that can be updated
            valid_fields = [
                'email', 'first_name', 'last_name', 'grade_level',
                'date_of_birth', 'phone_number', 'guardian_email', 'is_active'
            ]
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                elif field == 'password':
                    # Handle password updates with hashing
                    update_fields.append("password_hash = ?")
                    values.append(self._hash_password(value))
            
            if not update_fields:
                print("⚠️  No valid fields provided for update")
                return False
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(student_id)
            
            # Execute update query
            query = f"UPDATE students SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Student {student_id} updated successfully")
                return True
            else:
                print(f"⚠️  Student {student_id} not found")
                return False
                
        except sqlite3.IntegrityError as e:
            print(f"❌ Error updating student (constraint violation): {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error updating student: {e}")
            return False
        finally:
            conn.close()
    
    def delete_student(self, student_id: int, soft_delete: bool = True) -> bool:
        """
        Delete a student account (soft delete by default for data integrity).
        
        Args:
            student_id (int): Student's unique ID
            soft_delete (bool): If True, mark as inactive; if False, permanently delete
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if soft_delete:
                # Soft delete: mark as inactive
                cursor.execute("UPDATE students SET is_active = 0 WHERE id = ?", (student_id,))
                action = "deactivated"
            else:
                # Hard delete: permanently remove (will cascade to preferences)
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                action = "deleted"
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Student {student_id} {action} successfully")
                return True
            else:
                print(f"⚠️  Student {student_id} not found")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting student: {e}")
            return False
        finally:
            conn.close()
    
    # ==========================================
    # SUBJECT MANAGEMENT OPERATIONS
    # ==========================================
    
    def create_subject(self, name: str, category: str, difficulty_level: int, 
                      description: str = None, **kwargs) -> int:
        """
        Create a new subject/course in the catalog.
        
        Args:
            name (str): Subject name
            category (str): Subject category (STEM, Arts, etc.)
            difficulty_level (int): Difficulty level (1-5)
            description (str, optional): Subject description
            **kwargs: Optional fields (code, credits, prerequisites, etc.)
        
        Returns:
            int: Subject ID if successful, -1 if failed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Prepare optional fields
            code = kwargs.get('code')
            credits = kwargs.get('credits', 1)
            prerequisites = kwargs.get('prerequisites')
            teacher_name = kwargs.get('teacher_name')
            max_students = kwargs.get('max_students')
            semester = kwargs.get('semester')
            
            cursor.execute('''
                INSERT INTO subjects (name, code, description, category, difficulty_level,
                                    credits, prerequisites, teacher_name, max_students, semester)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, code, description, category, difficulty_level,
                  credits, prerequisites, teacher_name, max_students, semester))
            
            subject_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Subject created successfully with ID: {subject_id}")
            return subject_id
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Error creating subject (likely duplicate name/code): {e}")
            return -1
        except Exception as e:
            print(f"❌ Unexpected error creating subject: {e}")
            return -1
        finally:
            conn.close()
    
    def get_all_subjects(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve all subjects from the catalog.
        
        Args:
            active_only (bool): If True, only return active subjects
        
        Returns:
            List[Dict]: List of subject records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT id, name, code, description, category, difficulty_level,
                       credits, prerequisites, teacher_name, max_students, semester,
                       is_active, created_at
                FROM subjects
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY category, name'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'code': row[2],
                    'description': row[3],
                    'category': row[4],
                    'difficulty_level': row[5],
                    'credits': row[6],
                    'prerequisites': row[7],
                    'teacher_name': row[8],
                    'max_students': row[9],
                    'semester': row[10],
                    'is_active': row[11],
                    'created_at': row[12]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ Error retrieving subjects: {e}")
            return []
        finally:
            conn.close()
    
    def get_subjects_by_category(self, category: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve subjects filtered by category.
        
        Args:
            category (str): Subject category to filter by
            active_only (bool): If True, only return active subjects
        
        Returns:
            List[Dict]: List of subject records in the specified category
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT id, name, code, description, category, difficulty_level,
                       credits, prerequisites, teacher_name, max_students, semester,
                       is_active, created_at
                FROM subjects WHERE category = ?
            '''
            
            params = [category]
            
            if active_only:
                query += ' AND is_active = 1'
            
            query += ' ORDER BY name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'code': row[2],
                    'description': row[3],
                    'category': row[4],
                    'difficulty_level': row[5],
                    'credits': row[6],
                    'prerequisites': row[7],
                    'teacher_name': row[8],
                    'max_students': row[9],
                    'semester': row[10],
                    'is_active': row[11],
                    'created_at': row[12]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ Error retrieving subjects by category: {e}")
            return []
        finally:
            conn.close()
    
    # ==========================================
    # STUDENT PREFERENCES OPERATIONS
    # ==========================================
    
    def add_student_preference(self, student_id: int, subject_id: int, 
                             interest_level: int, priority: int = None, 
                             notes: str = None, status: str = 'interested') -> int:
        """
        Add or update a student's subject preference.
        
        Args:
            student_id (int): Student's unique ID
            subject_id (int): Subject's unique ID
            interest_level (int): Interest level (1-5)
            priority (int, optional): Priority ranking
            notes (str, optional): Additional notes
            status (str): Preference status (interested, enrolled, completed)
        
        Returns:
            int: Preference ID if successful, -1 if failed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Use INSERT OR REPLACE to handle duplicates
            cursor.execute('''
                INSERT OR REPLACE INTO student_preferences 
                (student_id, subject_id, interest_level, priority, notes, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, subject_id, interest_level, priority, notes, status))
            
            preference_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Preference added/updated successfully with ID: {preference_id}")
            return preference_id
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Error adding preference (foreign key constraint): {e}")
            return -1
        except Exception as e:
            print(f"❌ Unexpected error adding preference: {e}")
            return -1
        finally:
            conn.close()
    
    def get_student_preferences(self, student_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all preferences for a specific student.
        
        Args:
            student_id (int): Student's unique ID
        
        Returns:
            List[Dict]: List of student preferences with subject details
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT sp.id, sp.student_id, sp.subject_id, s.name as subject_name, 
                       s.code as subject_code, s.category, s.difficulty_level,
                       sp.interest_level, sp.priority, sp.notes, sp.status,
                       sp.created_at, sp.updated_at
                FROM student_preferences sp
                JOIN subjects s ON sp.subject_id = s.id
                WHERE sp.student_id = ? AND s.is_active = 1
                ORDER BY sp.priority ASC, sp.interest_level DESC
            ''', (student_id,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'student_id': row[1],
                    'subject_id': row[2],
                    'subject_name': row[3],
                    'subject_code': row[4],
                    'category': row[5],
                    'difficulty_level': row[6],
                    'interest_level': row[7],
                    'priority': row[8],
                    'notes': row[9],
                    'status': row[10],
                    'created_at': row[11],
                    'updated_at': row[12]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ Error retrieving student preferences: {e}")
            return []
        finally:
            conn.close()
    
    def remove_student_preference(self, student_id: int, subject_id: int) -> bool:
        """
        Remove a student's preference for a specific subject.
        
        Args:
            student_id (int): Student's unique ID
            subject_id (int): Subject's unique ID
        
        Returns:
            bool: True if removal successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM student_preferences 
                WHERE student_id = ? AND subject_id = ?
            ''', (student_id, subject_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Preference removed successfully")
                return True
            else:
                print(f"⚠️  Preference not found")
                return False
                
        except Exception as e:
            print(f"❌ Error removing preference: {e}")
            return False
        finally:
            conn.close()
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256 with salt.
        Note: In production, use bcrypt or similar for better security.
        
        Args:
            password (str): Plain text password
        
        Returns:
            str: Hashed password
        """
        # Add a salt for better security (in production, use random salt per password)
        salt = "student_subject_system_salt"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password
            password_hash (str): Stored password hash
        
        Returns:
            bool: True if password matches, False otherwise
        """
        return self._hash_password(password) == password_hash
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get basic statistics about the database contents.
        
        Returns:
            Dict[str, int]: Dictionary containing count statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Count active students
            cursor.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
            stats['active_students'] = cursor.fetchone()[0]
            
            # Count active subjects
            cursor.execute("SELECT COUNT(*) FROM subjects WHERE is_active = 1")
            stats['active_subjects'] = cursor.fetchone()[0]
            
            # Count total preferences
            cursor.execute("SELECT COUNT(*) FROM student_preferences")
            stats['total_preferences'] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
        finally:
            conn.close()

# Example usage and testing (only runs when script is executed directly)
if __name__ == "__main__":
    print("🧪 Testing Student CRUD Operations")
    print("=" * 40)
    
    try:
        # Initialize CRUD operations
        crud = StudentCRUD()
        
        # Display database statistics
        stats = crud.get_database_stats()
        print(f"Database Stats: {stats}")
        
        print("\n✅ CRUD operations ready for use")
        print("💡 Import this module to use CRUD operations in your application")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Run 'python scripts/database_setup.py' first to create the database")
    except Exception as e:
        print(f"❌ Error testing CRUD operations: {e}")
