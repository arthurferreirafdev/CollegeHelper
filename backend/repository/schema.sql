-- Student Subject Selection System Schema (PostgreSQL)

CREATE TABLE IF NOT EXISTS students (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    grade_level INTEGER CHECK (grade_level BETWEEN 9 AND 12),
    date_of_birth DATE,
    phone_number TEXT,
    guardian_email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE,
    description TEXT,
    category TEXT NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    credits INTEGER DEFAULT 1,
    prerequisites TEXT,
    teacher_name TEXT,
    max_students INTEGER,
    semester TEXT,
    schedule TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_preferences (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    interest_level INTEGER CHECK (interest_level BETWEEN 1 AND 5),
    priority INTEGER,
    notes TEXT,
    status TEXT DEFAULT 'interested',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_student_subject
        UNIQUE(student_id, subject_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_students_email 
    ON students(email);

CREATE INDEX IF NOT EXISTS idx_subjects_category 
    ON subjects(category);

CREATE INDEX IF NOT EXISTS idx_preferences_student 
    ON student_preferences(student_id);

CREATE INDEX IF NOT EXISTS idx_preferences_subject 
    ON student_preferences(subject_id);