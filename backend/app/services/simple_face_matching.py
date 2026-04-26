"""
Simple Face Matching Service for Cloud Deployment
Uses YOLOv8 for face detection only (no recognition)
For production, integrate with a face recognition API service
"""

import cv2
import numpy as np
from typing import Dict, List
from ultralytics import YOLO
import os

class SimpleFaceMatchingService:
    """Simple face detection service using YOLOv8 - no recognition"""
    
    def __init__(self):
        # Initialize YOLO model for face detection
        model_path = "app/yolov8n.pt" if os.path.exists("app/yolov8n.pt") else "yolov8n.pt"
        self.model = YOLO(model_path)
        self.confidence_threshold = 0.3
        
    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in an image using YOLOv8
        Returns: Number of faces detected
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Could not load image: {image_path}")
                return 0
            
            # Run YOLO detection
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            # Count detected faces (person class)
            faces_detected = 0
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    # Count detections (assuming person class = 0)
                    faces_detected = len(boxes)
            
            print(f"✅ Detected {faces_detected} faces in image")
            return faces_detected
            
        except Exception as e:
            print(f"❌ Error detecting faces: {e}")
            return 0
    
    async def process_attendance_simple(
        self, 
        image_path: str, 
        class_name: str,
        student_service
    ) -> Dict:
        """
        Process attendance using simple face detection
        This version only detects faces, doesn't identify them
        
        For production: Integrate with a face recognition API like:
        - Amazon Rekognition
        - Microsoft Azure Face API  
        - Google Cloud Vision API
        - DeepFace with cloud models
        """
        try:
            # Detect number of faces
            num_faces = self.detect_faces(image_path)
            
            # Get all students in the class
            all_students = await student_service.get_students_by_class(class_name)
            
            # For now, mark attendance based on face count
            # In production, you would use a face recognition API here
            present = []
            absent = []
            
            if num_faces > 0:
                # Mark first N students as present (placeholder logic)
                for i, student in enumerate(all_students):
                    if i < num_faces:
                        present.append({
                            'student_id': student['student_id'],
                            'name': student['name'],
                            'confidence': 0.0  # No actual recognition confidence
                        })
                    else:
                        absent.append({
                            'student_id': student['student_id'],
                            'name': student['name']
                        })
            else:
                # No faces detected, mark all absent
                absent = [{
                    'student_id': s['student_id'],
                    'name': s['name']
                } for s in all_students]
            
            return {
                'present': present,
                'absent': absent,
                'total_faces_detected': num_faces,
                'warning': 'Using basic face detection only. For accurate recognition, integrate a cloud face recognition API.'
            }
            
        except Exception as e:
            print(f"❌ Error processing attendance: {e}")
            # Return all students as absent on error
            all_students = await student_service.get_students_by_class(class_name)
            return {
                'present': [],
                'absent': [{
                    'student_id': s['student_id'],
                    'name': s['name']
                } for s in all_students],
                'total_faces_detected': 0,
                'error': str(e)
            }

# Global instance
simple_face_service = SimpleFaceMatchingService()
