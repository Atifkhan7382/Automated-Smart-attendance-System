"""
Verification Helper Functions

This module provides helper functions for teacher verification workflow:
- Storing verification candidates
- Retrieving pending verifications
- Processing teacher decisions
- Adding verified encodings
"""

import os
import base64
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import cv2

from app.models.database import DatabaseManager


class VerificationManager:
    """Manager for attendance verification operations"""
    
    def __init__(self):
        self.face_crops_dir = Path("data/verification_face_crops")
        self.face_crops_dir.mkdir(parents=True, exist_ok=True)
    
    def create_verification_record(
        self,
        attendance_record_id: int,
        face_index: int,
        face_crop: np.ndarray,
        bbox: Tuple[int, int, int, int],
        quality_score: float,
        suggested_student_id: Optional[str] = None,
        suggested_similarity: Optional[float] = None
    ) -> int:
        """
        Create a new verification record for uncertain match
        
        Args:
            attendance_record_id: ID of the attendance record
            face_index: Index of the face in the image
            face_crop: Cropped face image (numpy array)
            bbox: Bounding box (x1, y1, x2, y2)
            quality_score: Face quality score
            suggested_student_id: Top candidate student ID
            suggested_similarity: Similarity score with top candidate
            
        Returns:
            Verification record ID
        """
        # Save face crop
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        face_crop_filename = f"verification_{attendance_record_id}_{face_index}_{timestamp}.jpg"
        face_crop_path = self.face_crops_dir / face_crop_filename
        
        cv2.imwrite(str(face_crop_path), face_crop)
        
        # Insert verification record
        query = """
            INSERT INTO attendance_verifications (
                attendance_record_id, face_index, face_crop_path,
                bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                quality_score, suggested_student_id, suggested_similarity,
                verification_action
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """
        
        verification_id = DatabaseManager.execute_insert(
            query,
            (
                attendance_record_id, face_index, str(face_crop_path),
                bbox[0], bbox[1], bbox[2], bbox[3],
                quality_score, suggested_student_id, suggested_similarity
            )
        )
        
        return verification_id
    
    def get_pending_verifications(self, attendance_record_id: int) -> List[Dict]:
        """
        Get all pending verifications for an attendance record
        
        Args:
            attendance_record_id: ID of the attendance record
            
        Returns:
            List of pending verification records with face crops
        """
        query = """
            SELECT id, attendance_record_id, face_index, face_crop_path,
                   bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                   quality_score, suggested_student_id, suggested_similarity,
                   verification_action, verified_student_id, verified_at, encoding_added, created_at
            FROM attendance_verifications
            WHERE attendance_record_id = ? AND verification_action = 'pending'
            ORDER BY face_index
        """
        
        verifications = DatabaseManager.execute_query(query, (attendance_record_id,))
        
        # Get class name from attendance record
        attendance_query = "SELECT class_name FROM attendance_records WHERE id = ?"
        attendance_result = DatabaseManager.execute_query(attendance_query, (attendance_record_id,))
        class_name = attendance_result[0]['class_name'] if attendance_result else None
        
        # Get all students as potential candidates
        # Note: We get all students because class_name might not be properly set
        # The teacher will manually verify which student it actually is
        students_query = """
            SELECT student_id, name, class_name
            FROM students
            ORDER BY 
                CASE WHEN class_name = ? THEN 0 ELSE 1 END,
                name
            LIMIT 10
        """
        enrolled_students = DatabaseManager.execute_query(students_query, (class_name,)) if class_name else []
        
        # Convert to JSON-serializable format
        result = []
        
        # Helper function to safely convert values
        def safe_int(value):
            if value is None:
                return None
            if isinstance(value, bytes):
                # Convert bytes to int (little-endian)
                return int.from_bytes(value, byteorder='little')
            return int(value)
        
        def safe_float(value):
            if value is None:
                return 0.0
            if isinstance(value, bytes):
                return float(int.from_bytes(value, byteorder='little'))
            return float(value)
        
        def safe_str(value):
            if value is None:
                return None
            if isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore')
            return str(value)
        
        for verification in verifications:
            # Add base64 encoded face crop
            face_crop_base64 = None
            face_crop_path = safe_str(verification['face_crop_path'])
            if face_crop_path and os.path.exists(face_crop_path):
                with open(face_crop_path, 'rb') as f:
                    face_crop_bytes = f.read()
                    face_crop_base64 = f"data:image/jpeg;base64,{base64.b64encode(face_crop_bytes).decode('utf-8')}"
            
            # Build candidates list (top 3 enrolled students, with suggested student first)
            candidates = []
            suggested_student_id = safe_str(verification['suggested_student_id'])
            if suggested_student_id:
                # Add suggested student first
                suggested = next((s for s in enrolled_students if safe_str(s['student_id']) == suggested_student_id), None)
                if suggested:
                    candidates.append({
                        'student_id': safe_str(suggested['student_id']),
                        'name': safe_str(suggested['name']),
                        'similarity': safe_float(verification['suggested_similarity'])
                    })
            
            # Add other students (up to 3 total)
            for student in enrolled_students:
                if len(candidates) >= 3:
                    break
                if safe_str(student['student_id']) != suggested_student_id:
                    candidates.append({
                        'student_id': safe_str(student['student_id']),
                        'name': safe_str(student['name']),
                        'similarity': 0.0  # Unknown similarity for other students
                    })
            
            # Build JSON-serializable dict
            result.append({
                'id': safe_int(verification['id']),
                'attendance_record_id': safe_int(verification['attendance_record_id']),
                'face_index': safe_int(verification['face_index']),
                'face_crop_base64': face_crop_base64,
                'bbox': {
                    'x1': safe_int(verification['bbox_x1']),
                    'y1': safe_int(verification['bbox_y1']),
                    'x2': safe_int(verification['bbox_x2']),
                    'y2': safe_int(verification['bbox_y2'])
                },
                'quality_score': safe_float(verification['quality_score']),
                'suggested_student_id': suggested_student_id,
                'suggested_similarity': safe_float(verification['suggested_similarity']),
                'candidates': candidates,
                'verification_action': safe_str(verification['verification_action']),
                'verified_student_id': safe_str(verification['verified_student_id']),
                'verified_at': safe_str(verification['verified_at']),
                'encoding_added': bool(verification['encoding_added']),
                'created_at': safe_str(verification['created_at'])
            })
        
        return result
    
    def verify_face(
        self,
        verification_id: int,
        verified_student_id: Optional[str],
        action: str
    ) -> bool:
        """
        Process teacher's verification decision
        
        Args:
            verification_id: ID of the verification record
            verified_student_id: Student ID confirmed by teacher (None if rejected/unknown)
            action: 'approve', 'reject', or 'unknown'
            
        Returns:
            True if successful
        """
        query = """
            UPDATE attendance_verifications
            SET verified_student_id = ?,
                verification_action = ?,
                verified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        affected = DatabaseManager.execute_update(
            query,
            (verified_student_id, action, verification_id)
        )
        
        return affected > 0
    
    def mark_encoding_added(self, verification_id: int) -> bool:
        """
        Mark that encoding was successfully added from this verification
        
        Args:
            verification_id: ID of the verification record
            
        Returns:
            True if successful
        """
        query = """
            UPDATE attendance_verifications
            SET encoding_added = 1
            WHERE id = ?
        """
        
        affected = DatabaseManager.execute_update(query, (verification_id,))
        return affected > 0
    
    def get_verification_by_id(self, verification_id: int) -> Optional[Dict]:
        """
        Get verification record by ID
        
        Args:
            verification_id: ID of the verification record
            
        Returns:
            Verification record or None
        """
        query = "SELECT * FROM attendance_verifications WHERE id = ?"
        results = DatabaseManager.execute_query(query, (verification_id,))
        
        return results[0] if results else None
    
    def get_verification_stats(self, attendance_record_id: int) -> Dict:
        """
        Get verification statistics for an attendance record
        
        Args:
            attendance_record_id: ID of the attendance record
            
        Returns:
            Dictionary with verification stats
        """
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN verification_action = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN verification_action = 'approve' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN verification_action = 'reject' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN verification_action = 'unknown' THEN 1 ELSE 0 END) as unknown,
                SUM(CASE WHEN encoding_added = 1 THEN 1 ELSE 0 END) as encodings_added
            FROM attendance_verifications
            WHERE attendance_record_id = ?
        """
        
        results = DatabaseManager.execute_query(query, (attendance_record_id,))
        return results[0] if results else {}


# Global instance
verification_manager = VerificationManager()
