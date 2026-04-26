import sqlite3
import os
from datetime import datetime

# Determine database path
if os.path.exists("app/data"):
    DATABASE_PATH = "app/data/attendance.db"
elif os.path.exists("data"):
    DATABASE_PATH = "data/attendance.db"
else:
    DATABASE_PATH = "data/attendance.db"

def migrate_database():
    """Migrate existing database to new schema with authentication tables"""
    
    print("🔄 Starting database migration...")
    
    # Create data directory if it doesn't exist
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("✅ Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        else:
            print("ℹ️  Users table already exists")
        
        # Check if classes table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
        if not cursor.fetchone():
            print("✅ Creating classes table...")
            cursor.execute('''
                CREATE TABLE classes (
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_invite ON classes(invite_code)')
        else:
            print("ℹ️  Classes table already exists")
        
        # Check if class_enrollments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='class_enrollments'")
        if not cursor.fetchone():
            print("✅ Creating class_enrollments table...")
            cursor.execute('''
                CREATE TABLE class_enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(class_id, student_id)
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_class ON class_enrollments(class_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_student ON class_enrollments(student_id)')
        else:
            print("ℹ️  Class enrollments table already exists")
        
        # Check if students table has user_id column
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("✅ Adding user_id column to students table...")
            cursor.execute('ALTER TABLE students ADD COLUMN user_id INTEGER')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_user ON students(user_id)')
        else:
            print("ℹ️  Students table already has user_id column")
        
        # Check if attendance_records table has class_id column
        cursor.execute("PRAGMA table_info(attendance_records)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'class_id' not in columns:
            print("✅ Adding class_id column to attendance_records table...")
            cursor.execute('ALTER TABLE attendance_records ADD COLUMN class_id INTEGER')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_class_id ON attendance_records(class_id)')
        else:
            print("ℹ️  Attendance records table already has class_id column")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
