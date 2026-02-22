-- Student Subject Selection System Schema

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    grade_level INTEGER CHECK(grade_level >= 1), -- Corrigido para >= 1
    enrollment_number TEXT,                      -- Matrícula
    course_id INTEGER,                           -- Curso
    date_of_birth DATE,
    phone_number TEXT,
    guardian_email TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    coordinator TEXT,
    course_code TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE,
    description TEXT,
    category TEXT NOT NULL,
    course_id INTEGER, 
    difficulty_level INTEGER CHECK(difficulty_level >= 1 AND difficulty_level <= 5),
    credits INTEGER DEFAULT 1,
    prerequisites TEXT,
    teacher_name TEXT,
    max_students INTEGER,
    semester TEXT,
    schedule TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE IF NOT EXISTS student_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    interest_level INTEGER CHECK(interest_level >= 1 AND interest_level <= 5),
    priority INTEGER,
    notes TEXT,
    status TEXT DEFAULT 'interested',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,

    UNIQUE(student_id, subject_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_subjects_category ON subjects(category);
CREATE INDEX IF NOT EXISTS idx_preferences_student ON student_preferences(student_id);
CREATE INDEX IF NOT EXISTS idx_preferences_subject ON student_preferences(subject_id);
