from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.database import DatabaseManager
from app.core.security import generate_invite_code, INVITE_CODE_EXPIRE_DAYS

class ClassService:
    """Service for handling class management operations"""
    
    @staticmethod
    async def create_class(teacher_id: int, class_name: str, description: Optional[str] = None) -> Dict:
        """Create a new class"""
        import secrets
        import string
        
        # Generate invite code
        invite_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        
        # Create class with invite code
        class_id = DatabaseManager.execute_insert(
            """INSERT INTO classes (class_name, teacher_id, description, invite_code)
               VALUES (?, ?, ?, ?)""",
            (class_name, teacher_id, description, invite_code)
        )
        
        # Get created class
        class_data = DatabaseManager.execute_query(
            "SELECT * FROM classes WHERE id = ?",
            (class_id,)
        )
        
        if not class_data:
            raise ValueError("Failed to create class")
        
        return class_data[0]
    
    @staticmethod
    async def get_teacher_classes(teacher_id: int) -> List[Dict]:
        """Get all classes for a teacher"""
        classes = DatabaseManager.execute_query(
            """SELECT c.*, 
                      COUNT(DISTINCT ce.student_id) as student_count
               FROM classes c
               LEFT JOIN class_enrollments ce ON c.id = ce.class_id
               WHERE c.teacher_id = ?
               GROUP BY c.id
               ORDER BY c.created_at DESC""",
            (teacher_id,)
        )
        
        return classes
    
    @staticmethod
    async def get_class_by_id(class_id: int, teacher_id: Optional[int] = None) -> Optional[Dict]:
        """Get class by ID, optionally verify teacher ownership"""
        query = "SELECT * FROM classes WHERE id = ?"
        params = [class_id]
        
        if teacher_id is not None:
            query += " AND teacher_id = ?"
            params.append(teacher_id)
        
        classes = DatabaseManager.execute_query(query, tuple(params))
        
        if not classes:
            return None
        
        return classes[0]
    
    @staticmethod
    async def update_class(class_id: int, teacher_id: int, class_name: Optional[str] = None, 
                          description: Optional[str] = None) -> Dict:
        """Update class details"""
        # Verify ownership
        class_data = await ClassService.get_class_by_id(class_id, teacher_id)
        if not class_data:
            raise ValueError("Class not found or access denied")
        
        # Build update query
        updates = []
        params = []
        
        if class_name is not None:
            updates.append("class_name = ?")
            params.append(class_name)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if not updates:
            return class_data
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([class_id, teacher_id])
        
        query = f"UPDATE classes SET {', '.join(updates)} WHERE id = ? AND teacher_id = ?"
        DatabaseManager.execute_update(query, tuple(params))
        
        # Get updated class
        updated_class = await ClassService.get_class_by_id(class_id, teacher_id)
        return updated_class
    
    @staticmethod
    async def delete_class(class_id: int, teacher_id: int) -> bool:
        """Delete a class"""
        # Verify ownership
        class_data = await ClassService.get_class_by_id(class_id, teacher_id)
        if not class_data:
            raise ValueError("Class not found or access denied")
        
        # Delete class (cascade will handle enrollments)
        DatabaseManager.execute_update(
            "DELETE FROM classes WHERE id = ? AND teacher_id = ?",
            (class_id, teacher_id)
        )
        
        return True
    
    @staticmethod
    async def generate_invite_link(class_id: int, teacher_id: int, base_url: str = "http://localhost:3000") -> Dict:
        """Generate an invite link for a class"""
        # Verify ownership
        class_data = await ClassService.get_class_by_id(class_id, teacher_id)
        if not class_data:
            raise ValueError("Class not found or access denied")
        
        # Generate unique invite code
        invite_code = generate_invite_code()
        
        # Check if code already exists (very unlikely but possible)
        while DatabaseManager.execute_query("SELECT id FROM classes WHERE invite_code = ?", (invite_code,)):
            invite_code = generate_invite_code()
        
        # Set expiration date
        expires_at = datetime.now() + timedelta(days=INVITE_CODE_EXPIRE_DAYS)
        
        # Update class with invite code
        DatabaseManager.execute_update(
            """UPDATE classes 
               SET invite_code = ?, invite_expires_at = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (invite_code, expires_at.isoformat(), class_id)
        )
        
        # Generate invite URL
        invite_url = f"{base_url}/register/student?invite={invite_code}"
        
        return {
            "invite_code": invite_code,
            "invite_url": invite_url,
            "expires_at": expires_at.isoformat()
        }
    
    @staticmethod
    async def get_class_students(class_id: int, teacher_id: int) -> List[Dict]:
        """Get all students enrolled in a class"""
        # Verify ownership
        class_data = await ClassService.get_class_by_id(class_id, teacher_id)
        if not class_data:
            raise ValueError("Class not found or access denied")
        
        students = DatabaseManager.execute_query(
            """SELECT s.student_id, s.name, u.email, u.full_name, ce.enrolled_at,
                      COUNT(DISTINCT sa.id) as total_sessions,
                      SUM(CASE WHEN sa.status = 'present' THEN 1 ELSE 0 END) as present_count
               FROM class_enrollments ce
               JOIN students s ON ce.student_id = s.student_id
               JOIN users u ON s.user_id = u.id
               LEFT JOIN student_attendance sa ON sa.student_id = s.student_id
               WHERE ce.class_id = ?
               GROUP BY s.student_id, s.name, u.email, u.full_name, ce.enrolled_at
               ORDER BY s.name""",
            (class_id,)
        )
        
        # Calculate attendance percentage
        result = []
        for student in students:
            total = student.get('total_sessions', 0)
            present = student.get('present_count', 0)
            percentage = (present / total * 100) if total > 0 else 0.0
            
            result.append({
                "student_id": student['student_id'],
                "student_name": student['name'],
                "student_email": student['email'],
                "student_number": student.get('student_id', ''),
                "enrolled_at": student['enrolled_at'],
                "attendance_percentage": round(percentage, 2)
            })
        
        return result
    
    @staticmethod
    async def remove_student_from_class(class_id: int, student_id: int, teacher_id: int) -> bool:
        """Remove a student from a class"""
        # Verify ownership
        class_data = await ClassService.get_class_by_id(class_id, teacher_id)
        if not class_data:
            raise ValueError("Class not found or access denied")
        
        # Remove enrollment
        affected = DatabaseManager.execute_update(
            "DELETE FROM class_enrollments WHERE class_id = ? AND student_id = ?",
            (class_id, student_id)
        )
        
        return affected > 0
    
    @staticmethod
    async def get_student_classes(student_id: int) -> List[Dict]:
        """Get all classes a student is enrolled in"""
        classes = DatabaseManager.execute_query(
            """SELECT c.id, c.class_name, c.description, c.created_at, ce.enrolled_at,
                      u.full_name as teacher_name
               FROM class_enrollments ce
               JOIN classes c ON ce.class_id = c.id
               JOIN users u ON c.teacher_id = u.id
               WHERE ce.student_id = ?
               ORDER BY ce.enrolled_at DESC""",
            (student_id,)
        )
        
        return classes
    
    @staticmethod
    async def verify_class_access(class_id: int, user_id: int, role: str) -> bool:
        """Verify if a user has access to a class"""
        if role == "teacher":
            # Check if user is the teacher of this class
            class_data = await ClassService.get_class_by_id(class_id, user_id)
            return class_data is not None
        elif role == "student":
            # Check if user is enrolled in this class
            enrollment = DatabaseManager.execute_query(
                "SELECT id FROM class_enrollments WHERE class_id = ? AND student_id = ?",
                (class_id, user_id)
            )
            return len(enrollment) > 0
        
        return False
