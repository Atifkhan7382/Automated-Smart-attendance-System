"""
Check database schema and students
"""
import sqlite3
import os

def check_database():
    """Check students in database"""
    db_path = "data/attendance.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
    schema = cursor.fetchone()
    print("="*100)
    print("STUDENTS TABLE SCHEMA")
    print("="*100)
    print(schema[0] if schema else "Table not found")
    print()
    
    # Get all students
    cursor.execute("""
        SELECT student_id, name, class_name, created_at
        FROM students
        ORDER BY class_name, name
    """)
    
    students = cursor.fetchall()
    
    print("="*100)
    print("ALL STUDENTS IN DATABASE")
    print("="*100)
    print(f"{'ID':<10} {'Name':<20} {'Class':<15} {'Created At':<25}")
    print("-"*100)
    
    for student_id, name, class_name, created_at in students:
        print(f"{student_id:<10} {name:<20} {class_name:<15} {created_at:<25}")
    
    print(f"\nTotal students: {len(students)}")
    
    # Get students by class
    cursor.execute("""
        SELECT class_name, COUNT(*) as count
        FROM students
        GROUP BY class_name
    """)
    
    class_counts = cursor.fetchall()
    
    print("\n" + "="*100)
    print("STUDENTS BY CLASS")
    print("="*100)
    for class_name, count in class_counts:
        print(f"{class_name}: {count} students")
    
    # Get recent attendance records
    cursor.execute("""
        SELECT a.id, a.class_name, a.marked_at, COUNT(ar.student_id) as present_count
        FROM attendance a
        LEFT JOIN attendance_records ar ON a.id = ar.attendance_id
        GROUP BY a.id
        ORDER BY a.marked_at DESC
        LIMIT 5
    """)
    
    attendance_records = cursor.fetchall()
    
    print("\n" + "="*100)
    print("RECENT ATTENDANCE RECORDS")
    print("="*100)
    print(f"{'ID':<10} {'Class':<15} {'Marked At':<25} {'Present Count':<15}")
    print("-"*100)
    
    for att_id, class_name, marked_at, present_count in attendance_records:
        print(f"{att_id:<10} {class_name:<15} {marked_at:<25} {present_count:<15}")
    
    # Get details of last attendance
    if attendance_records:
        last_att_id = attendance_records[0][0]
        cursor.execute("""
            SELECT ar.student_id, s.name, ar.confidence
            FROM attendance_records ar
            JOIN students s ON ar.student_id = s.student_id
            WHERE ar.attendance_id = ?
        """, (last_att_id,))
        
        present_students = cursor.fetchall()
        
        print(f"\nLast Attendance (ID: {last_att_id}) - Present Students:")
        for student_id, name, confidence in present_students:
            print(f"  - {name} (ID: {student_id}, Confidence: {confidence:.2f})")
    
    conn.close()

if __name__ == "__main__":
    check_database()
