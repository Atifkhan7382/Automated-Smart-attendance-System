"""
Helper method for attendance verification
"""
from datetime import datetime
from app.models.database import DatabaseManager

async def add_verified_student(attendance_id: int, student_id: str) -> bool:
    """
    Add a verified student to attendance record (mark as present)
    Used when teacher manually verifies a face match
    
    Args:
        attendance_id: ID of the attendance record
        student_id: Student ID to mark as present
        
    Returns:
        True if successful
    """
    try:
        db = DatabaseManager()
        current_time = datetime.now().isoformat()
        
        # Check if student already has an attendance record for this session
        check_query = """
            SELECT id, status FROM student_attendance
            WHERE attendance_record_id = ? AND student_id = ?
        """
        existing = db.execute_query(check_query, (attendance_id, student_id))
        
        if existing:
            # Update existing record to present
            update_query = """
                UPDATE student_attendance
                SET status = 'present', confidence = 1.0, created_at = ?
                WHERE id = ?
            """
            db.execute_update(update_query, (current_time, existing[0]['id']))
            print(f"✅ Updated student {student_id} to present in attendance {attendance_id}")
        else:
            # Insert new attendance record
            insert_query = """
                INSERT INTO student_attendance (attendance_record_id, student_id, status, confidence, created_at)
                VALUES (?, ?, 'present', 1.0, ?)
            """
            db.execute_insert(insert_query, (attendance_id, student_id, current_time))
            print(f"✅ Added student {student_id} as present in attendance {attendance_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding verified student: {e}")
        return False
