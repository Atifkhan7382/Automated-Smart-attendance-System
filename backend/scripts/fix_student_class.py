import sqlite3
import os

db_path = "data/attendance.db"

def fix_student_classes():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Before update:")
    cursor.execute("SELECT student_id, name, class_name FROM students WHERE student_id IN ('118', '23')")
    for row in cursor.fetchall():
        print(row)
        
    print("\nUpdating class to 'AI'...")
    cursor.execute("UPDATE students SET class_name = 'AI' WHERE student_id IN ('118', '23')")
    conn.commit()
    
    print(f"Updated {cursor.rowcount} students.")
    
    print("\nAfter update:")
    cursor.execute("SELECT student_id, name, class_name FROM students WHERE student_id IN ('118', '23')")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    fix_student_classes()
