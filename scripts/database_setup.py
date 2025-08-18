"""
DATABASE SETUP MODULE
====================
This module handles the creation and initialization of the SQLite database
for the student subject selection system. It creates the necessary tables
with proper relationships and constraints, but does not include any sample data.

Tables created:
- students: Store student account information
- subjects: Store available subjects/courses
- student_preferences: Store student subject preferences (many-to-many relationship)

Usage:
    python scripts/database_setup.py
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

class DatabaseSetup:
    """
    Handles database creation and schema setup for the student subject system.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database setup with configurable path.
        
        Args:
            db_path (str, optional): Custom database path. Defaults to 'data/student_subjects.db'
        """
        # Use environment variable or default path
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'data/student_subjects.db')
        
        # Ensure data directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def create_database(self) -> bool:
        """
        Create the database and all required tables with proper schema.
        
        Returns:
            bool: True if database creation was successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create students table - stores user account information
            self._create_students_table(cursor)
            
            # Create subjects table - stores available courses/subjects
            self._create_subjects_table(cursor)
            
            # Create student_preferences table - many-to-many relationship
            self._create_preferences_table(cursor)
            
            # Create indexes for better query performance
            self._create_indexes(cursor)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Database created successfully at: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating database: {str(e)}")
            return False
    
    def _create_students_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create the students table with all necessary fields and constraints.
        
        Args:
            cursor: SQLite cursor object
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,                    -- Student email (login username)
                password_hash TEXT NOT NULL,                   -- Hashed password for security
                first_name TEXT NOT NULL,                      -- Student first name
                last_name TEXT NOT NULL,                       -- Student last name
                grade_level INTEGER CHECK(grade_level >= 9 AND grade_level <= 12), -- Grade 9-12
                date_of_birth DATE,                           -- Optional date of birth
                phone_number TEXT,                            -- Optional contact number
                guardian_email TEXT,                          -- Optional parent/guardian email
                is_active BOOLEAN DEFAULT 1,                 -- Account status
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_subjects_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create the subjects table to store available courses.
        
        Args:
            cursor: SQLite cursor object
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,                    -- Subject name (e.g., "Mathematics")
                code TEXT UNIQUE,                             -- Subject code (e.g., "MATH101")
                description TEXT,                             -- Detailed subject description
                category TEXT NOT NULL,                       -- Subject category (STEM, Arts, etc.)
                difficulty_level INTEGER CHECK(difficulty_level >= 1 AND difficulty_level <= 5), -- 1-5 scale
                credits INTEGER DEFAULT 1,                    -- Credit hours/points
                prerequisites TEXT,                           -- Required prerequisite subjects
                teacher_name TEXT,                            -- Assigned teacher
                max_students INTEGER,                         -- Maximum enrollment
                semester TEXT,                                -- Available semester
                is_active BOOLEAN DEFAULT 1,                 -- Subject availability status
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_preferences_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create the student_preferences table for many-to-many relationship.
        
        Args:
            cursor: SQLite cursor object
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,                  -- Foreign key to students table
                subject_id INTEGER NOT NULL,                  -- Foreign key to subjects table
                interest_level INTEGER CHECK(interest_level >= 1 AND interest_level <= 5), -- 1-5 scale
                priority INTEGER,                             -- Student's priority ranking
                notes TEXT,                                   -- Additional student notes
                status TEXT DEFAULT 'interested',            -- Status: interested, enrolled, completed
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign key constraints with cascade delete
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
                
                -- Ensure unique student-subject combinations
                UNIQUE(student_id, subject_id)
            )
        ''')
    
    def _create_indexes(self, cursor: sqlite3.Cursor) -> None:
        """
        Create database indexes for improved query performance.
        
        Args:
            cursor: SQLite cursor object
        """
        # Index on student email for login queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_email ON students(email)')
        
        # Index on subject category for filtering
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subjects_category ON subjects(category)')
        
        # Index on student_preferences for quick lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_preferences_student ON student_preferences(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_preferences_subject ON student_preferences(subject_id)')
    
    def verify_database(self) -> bool:
        """
        Verify that the database was created correctly by checking table existence.
        
        Returns:
            bool: True if all tables exist, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if all required tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('students', 'subjects', 'student_preferences')
            """)
            
            tables = cursor.fetchall()
            conn.close()
            
            expected_tables = {'students', 'subjects', 'student_preferences'}
            found_tables = {table[0] for table in tables}
            
            if expected_tables.issubset(found_tables):
                print("✅ Database verification successful - all tables exist")
                return True
            else:
                missing = expected_tables - found_tables
                print(f"❌ Database verification failed - missing tables: {missing}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying database: {str(e)}")
            return False

def main():
    """
    Main function to create and verify the database.
    Can be run directly or imported as a module.
    """
    print("🗄️  Setting up Student Subject Selection Database")
    print("=" * 50)
    
    # Initialize database setup
    db_setup = DatabaseSetup()
    
    # Create database and tables
    if db_setup.create_database():
        # Verify the database was created correctly
        if db_setup.verify_database():
            print("\n🎉 Database setup completed successfully!")
            print(f"📍 Database location: {db_setup.db_path}")
            print("\nNext steps:")
            print("1. Configure your application to use this database")
            print("2. Add subjects through the admin interface")
            print("3. Students can now register and select preferences")
        else:
            print("\n❌ Database setup failed verification")
    else:
        print("\n❌ Database setup failed")

if __name__ == "__main__":
    main()
