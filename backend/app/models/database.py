import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional

# Determine the correct database path based on current working directory
if os.path.exists("app/data"):
    # Running from backend/ directory
    DATABASE_PATH = "app/data/attendance.db"
elif os.path.exists("backend/data/attendance.db"):
    # Running from repo root
    DATABASE_PATH = "backend/data/attendance.db"
elif os.path.exists("data/attendance.db"):
    # Running from app/ directory
    DATABASE_PATH = "data/attendance.db"
else:
    # Default path
    DATABASE_PATH = "data/attendance.db"

def get_db_connection():
    """Get database connection"""
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table (for authentication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT CHECK(role IN ('teacher', 'student')) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Classes table (teacher-owned classes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            description TEXT,
            invite_code TEXT UNIQUE,
            invite_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Class enrollments table (student-class relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(class_id, student_id)
        )
    ''')
    
    # Students table (updated to link with users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            image_path TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')
    
    # Attendance records table (updated to link with classes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            class_name TEXT NOT NULL,
            date DATE NOT NULL,
            image_path TEXT,
            total_faces_detected INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE SET NULL
        )
    ''')
    
    # Student attendance table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_record_id INTEGER,
            student_id TEXT,
            status TEXT CHECK(status IN ('present', 'absent')) NOT NULL,
            confidence REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (attendance_record_id) REFERENCES attendance_records (id),
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Attendance verifications table (for teacher-in-the-loop verification)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_record_id INTEGER NOT NULL,
            face_index INTEGER NOT NULL,
            face_crop_path TEXT,
            bbox_x1 INTEGER,
            bbox_y1 INTEGER,
            bbox_x2 INTEGER,
            bbox_y2 INTEGER,
            quality_score REAL,
            suggested_student_id TEXT,
            suggested_similarity REAL,
            verified_student_id TEXT,
            verification_action TEXT CHECK(verification_action IN ('approve', 'reject', 'unknown', 'pending')),
            verified_at TIMESTAMP,
            encoding_added BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (attendance_record_id) REFERENCES attendance_records (id) ON DELETE CASCADE,
            FOREIGN KEY (suggested_student_id) REFERENCES students (student_id),
            FOREIGN KEY (verified_student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_invite ON classes(invite_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_class ON class_enrollments(class_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_student ON class_enrollments(student_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_user ON students(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_class ON attendance_records(class_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_class_id ON attendance_records(class_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_attendance_record ON student_attendance(attendance_record_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_attendance_student ON student_attendance(student_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verifications_attendance ON attendance_verifications(attendance_record_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verifications_action ON attendance_verifications(verification_action)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

class DatabaseManager:
    """Database manager class for common operations"""
    
    @staticmethod
    def get_db_connection():
        """Get database connection for manual operations"""
        return get_db_connection()
    
    @staticmethod
    def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute a SELECT query and return results as list of dictionaries"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        return [dict(row) for row in rows]
    
    @staticmethod
    def execute_insert(query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT query and return the last row id"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        last_row_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        
        return last_row_id
    
    @staticmethod
    def execute_update(query: str, params: Optional[tuple] = None) -> int:
        """Execute an UPDATE/DELETE query and return number of affected rows"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows