from typing import List, Dict, Optional
from datetime import datetime
from app.models.database import DatabaseManager
from app.services.video_processing import VideoProcessingService
import os
import shutil

class StudentManagementService:
    """Service for managing student data"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.video_processor = VideoProcessingService()
    
    async def create_student(self, name: str, student_id: str, class_name: str, image_path: str) -> Dict:
        """Create a new student record"""
        try:
            # Check if student already exists
            existing_student = await self.get_student_by_id(student_id)
            if existing_student:
                raise ValueError(f"Student with ID {student_id} already exists")
            
            # Insert student into database
            query = """
                INSERT INTO students (student_id, name, class_name, image_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            current_time = datetime.now().isoformat()
            params = (student_id, name, class_name, image_path, current_time, current_time)
            
            self.db.execute_insert(query, params)
            
            # Return the created student
            return await self.get_student_by_id(student_id)
            
        except Exception as e:
            print(f"Error creating student: {e}")
            raise e
    
    async def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get a student by their ID"""
        try:
            query = "SELECT * FROM students WHERE student_id = ?"
            results = self.db.execute_query(query, (student_id,))
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            print(f"Error getting student by ID: {e}")
            return None
    
    async def get_students(self, class_name: Optional[str] = None) -> List[Dict]:
        """Get all students, optionally filtered by class"""
        try:
            if class_name:
                query = "SELECT * FROM students WHERE class_name = ? ORDER BY name"
                results = self.db.execute_query(query, (class_name,))
            else:
                query = "SELECT * FROM students ORDER BY class_name, name"
                results = self.db.execute_query(query)
            
            return results
            
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    async def get_enrolled_students(self, class_name: str) -> List[Dict]:
        """Get students enrolled in a class via the enrollment table"""
        try:
            # Join students with class_enrollments and classes tables
            query = """
                SELECT DISTINCT s.* 
                FROM students s
                INNER JOIN class_enrollments ce ON s.student_id = ce.student_id
                INNER JOIN classes c ON ce.class_id = c.id
                WHERE c.class_name = ?
                ORDER BY s.name
            """
            results = self.db.execute_query(query, (class_name,))
            return results
            
        except Exception as e:
            print(f"Error getting enrolled students: {e}")
            return []

    
    async def update_student(self, student_id: str, name: Optional[str] = None, 
                           class_name: Optional[str] = None, image_path: Optional[str] = None) -> Dict:
        """Update student information"""
        try:
            # Check if student exists
            existing_student = await self.get_student_by_id(student_id)
            if not existing_student:
                raise ValueError(f"Student with ID {student_id} not found")
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = ?")
                params.append(name)
            
            if class_name is not None:
                update_fields.append("class_name = ?")
                params.append(class_name)
            
            if image_path is not None:
                update_fields.append("image_path = ?")
                params.append(image_path)
            
            if not update_fields:
                return existing_student  # No updates needed
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(student_id)  # For WHERE clause
            
            query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = ?"
            self.db.execute_update(query, tuple(params))
            
            # Return updated student
            return await self.get_student_by_id(student_id)
            
        except Exception as e:
            print(f"Error updating student: {e}")
            raise e
    
    async def delete_student(self, student_id: str) -> bool:
        """Delete a student record"""
        try:
            # Check if student exists
            existing_student = await self.get_student_by_id(student_id)
            if not existing_student:
                raise ValueError(f"Student with ID {student_id} not found")
            
            # Delete from student_attendance first (foreign key constraint)
            self.db.execute_update("DELETE FROM student_attendance WHERE student_id = ?", (student_id,))
            
            # Delete student record
            affected_rows = self.db.execute_update("DELETE FROM students WHERE student_id = ?", (student_id,))
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error deleting student {student_id}: {e}")
            raise e
    
    async def clear_all_students(self) -> bool:
        """Clear all students and their data"""
        try:
            # Delete all students from database
            self.db.execute_query("DELETE FROM students")
            
            # Clean up student images directory
            import shutil
            student_images_dir = "data/student_images"
            if os.path.exists(student_images_dir):
                shutil.rmtree(student_images_dir)
                os.makedirs(student_images_dir, exist_ok=True)
            
            print("Cleared all students")
            return True
            
        except Exception as e:
            print(f"Error clearing all students: {e}")
            return False
    
    async def get_classes(self) -> List[str]:
        """Get list of all unique class names"""
        try:
            query = "SELECT DISTINCT class_name FROM students ORDER BY class_name"
            results = self.db.execute_query(query)
            
            return [row['class_name'] for row in results]
            
        except Exception as e:
            print(f"Error getting classes: {e}")
            return []
    
    async def get_class_statistics(self, class_name: str) -> Dict:
        """Get statistics for a specific class"""
        try:
            # Get total students in class
            total_query = "SELECT COUNT(*) as total FROM students WHERE class_name = ?"
            total_result = self.db.execute_query(total_query, (class_name,))
            total_students = total_result[0]['total'] if total_result else 0
            
            # Get recent attendance data (last 30 days)
            attendance_query = """
                SELECT 
                    COUNT(DISTINCT ar.id) as total_sessions,
                    COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as total_present,
                    COUNT(sa.id) as total_records
                FROM attendance_records ar
                LEFT JOIN student_attendance sa ON ar.id = sa.attendance_record_id
                WHERE ar.class_name = ? AND ar.date >= date('now', '-30 days')
            """
            attendance_result = self.db.execute_query(attendance_query, (class_name,))
            
            stats = {
                'class_name': class_name,
                'total_students': total_students,
                'total_sessions': 0,
                'attendance_rate': 0.0
            }
            
            if attendance_result:
                result = attendance_result[0]
                stats['total_sessions'] = result['total_sessions'] or 0
                total_records = result['total_records'] or 0
                total_present = result['total_present'] or 0
                
                if total_records > 0:
                    stats['attendance_rate'] = (total_present / total_records) * 100
            
            return stats
            
        except Exception as e:
            print(f"Error getting class statistics: {e}")
            return {
                'class_name': class_name,
                'total_students': 0,
                'total_sessions': 0,
                'attendance_rate': 0.0
            }
    
    async def search_students(self, search_term: str) -> List[Dict]:
        """Search students by name or student ID"""
        try:
            query = """
                SELECT * FROM students 
                WHERE name LIKE ? OR student_id LIKE ? 
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            results = self.db.execute_query(query, (search_pattern, search_pattern))
            
            return results
            
        except Exception as e:
            print(f"Error searching students: {e}")
            return []
    
    async def create_student_from_video(self, name: str, student_id: str, class_name: str, video_path: str) -> Dict:
        """Create a new student record from video upload"""
        try:
            # Check if student already exists
            existing_student = await self.get_student_by_id(student_id)
            if existing_student:
                raise ValueError(f"Student with ID {student_id} already exists")
            
            # Validate video
            video_validation = self.video_processor.validate_video(video_path)
            if not video_validation["valid"]:
                raise ValueError(f"Invalid video: {video_validation['error']}")
            
            # Process video and extract frames
            video_result = self.video_processor.process_student_video(
                video_path, student_id, name, class_name
            )
            
            if not video_result["success"]:
                raise ValueError(f"Video processing failed: {video_result['error']}")
            
            # Create student directory structure
            student_dir = os.path.join("data/student_images", student_id)
            os.makedirs(student_dir, exist_ok=True)
            
            # Save video file to student directory
            video_filename = f"{student_id}_enrollment_video.mp4"
            video_destination = os.path.join(student_dir, video_filename)
            shutil.move(video_path, video_destination)
            
            # Create student record in database
            query = """
                INSERT INTO students (student_id, name, class_name, image_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            current_time = datetime.now().isoformat()
            params = (student_id, name, class_name, student_dir, current_time, current_time)
            
            self.db.execute_insert(query, params)
            
            # Return comprehensive result
            result = {
                "success": True,
                "student": await self.get_student_by_id(student_id),
                "video_processing": video_result,
                "video_validation": video_validation,
                "frames_extracted": video_result["frames_extracted"],
                "frame_paths": video_result["frame_paths"]
            }
            
            print(f"Created student {name} ({student_id}) from video with {video_result['frames_extracted']} frames")
            return result
            
        except Exception as e:
            print(f"Error creating student from video: {e}")
            # Clean up on failure
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                student_dir = os.path.join("data/student_images", student_id)
                if os.path.exists(student_dir):
                    shutil.rmtree(student_dir)
            except:
                pass
            raise e