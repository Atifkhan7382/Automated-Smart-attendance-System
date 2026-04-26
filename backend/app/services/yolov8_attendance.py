"""
YOLOv8 Face Detection + Face Matching for Attendance
Works locally without Azure - uses YOLOv8 to detect faces and OpenCV to match them
"""

import cv2
import numpy as np
import os
import pickle
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YOLOv8AttendanceService:
    """
    Complete attendance system using:
    1. YOLOv8 for face detection
    2. Face embeddings for recognition/matching
    """
    
    def __init__(self, student_service):
        self.student_service = student_service
        
        # Load YOLOv8 model (force CPU to avoid CUDA compatibility issues)
        model_path = self._find_yolo_model()
        self.yolo_model = YOLO(model_path)
        self.yolo_model.to('cpu')  # Force CPU usage
        
        # Face recognition settings
        self.confidence_threshold = 0.25  # YOLO detection confidence
        self.match_threshold = 0.85  # Face matching threshold (INCREASED from 0.6 to 0.85 to reduce false positives)
        
        # Load trained face data if exists
        self.encodings_file = "backend/data/encodings/yolov8_face_encodings.pkl"
        if not os.path.exists(self.encodings_file):
            self.encodings_file = "data/encodings/yolov8_face_encodings.pkl"
        
        self.student_faces = {}  # student_id -> face_descriptor
        self.load_face_encodings()
        
        logger.info(f"✅ YOLOv8 Attendance Service initialized")
        logger.info(f"   Loaded {len(self.student_faces)} student face encodings")
    
    def _find_yolo_model(self) -> str:
        """Find YOLOv8 model file"""
        possible_paths = [
            "backend/app/yolov8n.pt",
            "app/yolov8n.pt",
            "backend/yolov8n.pt",
            "yolov8n.pt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found YOLO model at: {path}")
                return path
        
        logger.warning("YOLO model not found, will download default")
        return "yolov8n.pt"
    
    def load_face_encodings(self):
        """Load pre-computed face encodings for all students"""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.student_faces = data.get('encodings', {})
                    logger.info(f"✅ Loaded {len(self.student_faces)} face encodings from {self.encodings_file}")
            except Exception as e:
                logger.warning(f"Could not load face encodings: {e}")
                self.student_faces = {}
        else:
            logger.info("No face encodings file found. Students need to be enrolled first.")
            self.student_faces = {}
    
    def compute_face_descriptor(self, face_image: np.ndarray) -> np.ndarray:
        """
        Compute face descriptor/embedding from face image
        Using simple histogram-based method (works without insightface)
        """
        # Resize to standard size
        face_resized = cv2.resize(face_image, (128, 128))
        
        # Convert to grayscale
        if len(face_resized.shape) == 3:
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_resized
        
        # Compute histogram as simple descriptor
        hist = cv2.calcHist([face_gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Also add LBP features
        lbp = self._compute_lbp(face_gray)
        
        # Combine features
        descriptor = np.concatenate([hist, lbp])
        
        return descriptor
    
    def _compute_lbp(self, image: np.ndarray) -> np.ndarray:
        """Compute Local Binary Pattern features"""
        # Simple LBP implementation
        rows, cols = image.shape
        lbp_image = np.zeros_like(image)
        
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                center = image[i, j]
                code = 0
                
                # 8 neighbors
                code |= (image[i-1, j-1] > center) << 7
                code |= (image[i-1, j] > center) << 6
                code |= (image[i-1, j+1] > center) << 5
                code |= (image[i, j+1] > center) << 4
                code |= (image[i+1, j+1] > center) << 3
                code |= (image[i+1, j] > center) << 2
                code |= (image[i+1, j-1] > center) << 1
                code |= (image[i, j-1] > center) << 0
                
                lbp_image[i, j] = code
        
        # Compute histogram
        hist = cv2.calcHist([lbp_image], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        return hist
    
    def match_face(self, face_descriptor: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Match a face descriptor against known students
        Returns (student_id, confidence) or (None, 0.0)
        """
        if not self.student_faces:
            return None, 0.0
        
        best_match_id = None
        best_similarity = 0.0
        
        for student_id, stored_descriptor in self.student_faces.items():
            # Compute cosine similarity
            similarity = np.dot(face_descriptor, stored_descriptor) / (
                np.linalg.norm(face_descriptor) * np.linalg.norm(stored_descriptor)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = student_id
        
        # Check if similarity is above threshold
        if best_similarity >= self.match_threshold:
            return best_match_id, float(best_similarity)
        else:
            return None, float(best_similarity)
    
    async def enroll_student_faces(self, student_id: str, image_path: str) -> bool:
        """
        Enroll a student by extracting and storing their face descriptor
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return False
            
            # Detect faces with YOLOv8
            results = self.yolo_model(image, conf=self.confidence_threshold, verbose=False)
            
            if not results or len(results) == 0:
                logger.warning(f"No faces detected in {image_path}")
                return False
            
            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                logger.warning(f"No face boxes found in {image_path}")
                return False
            
            # Use the first detected face
            box = boxes[0].xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, box)
            
            # Extract face region
            face_image = image[y1:y2, x1:x2]
            
            if face_image.size == 0:
                logger.warning(f"Empty face region extracted")
                return False
            
            # Compute face descriptor
            descriptor = self.compute_face_descriptor(face_image)
            
            # Store descriptor
            self.student_faces[student_id] = descriptor
            
            # Save to file
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            with open(self.encodings_file, 'wb') as f:
                pickle.dump({'encodings': self.student_faces}, f)
            
            logger.info(f"✅ Enrolled student {student_id} - face descriptor saved")
            return True
            
        except Exception as e:
            logger.error(f"Error enrolling student {student_id}: {e}")
            return False
    
    async def process_attendance_image(self, image_path: str, class_name: str) -> Dict:
        """
        Process attendance image:
        1. Detect all faces with YOLOv8
        2. Match each face against enrolled students
        3. Mark attendance
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Detect faces with YOLOv8
            results = self.yolo_model(image, conf=self.confidence_threshold, verbose=False)
            
            num_faces = 0
            detected_students = []
            unknown_faces = 0
            
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    num_faces = len(boxes)
                    logger.info(f"🔍 YOLOv8 detected {num_faces} faces")
                    
                    # Process each detected face
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        
                        # Extract face region
                        face_image = image[y1:y2, x1:x2]
                        
                        if face_image.size == 0:
                            continue
                        
                        # Compute face descriptor
                        descriptor = self.compute_face_descriptor(face_image)
                        
                        # Match against known students
                        student_id, confidence = self.match_face(descriptor)
                        
                        if student_id:
                            # Get student info
                            all_students = await self.student_service.get_students(class_name)
                            student_info = next(
                                (s for s in all_students if s['student_id'] == student_id), 
                                None
                            )
                            
                            if student_info:
                                detected_students.append({
                                    'student_id': student_id,
                                    'name': student_info['name'],
                                    'confidence': round(confidence, 2),
                                    'bbox': [x1, y1, x2, y2]
                                })
                                logger.info(f"   ✅ Recognized: {student_info['name']} (confidence: {confidence:.2f})")
                        else:
                            unknown_faces += 1
                            logger.info(f"   ❓ Unknown face (confidence: {confidence:.2f})")
            
            # Get all students in class
            all_students = await self.student_service.get_students(class_name)
            
            # Deduplicate detected students (keep highest confidence for each student)
            unique_students = {}
            for student in detected_students:
                student_id = student['student_id']
                if student_id not in unique_students or student['confidence'] > unique_students[student_id]['confidence']:
                    unique_students[student_id] = student
            
            # Convert back to list
            present = list(unique_students.values())
            present_ids = list(unique_students.keys())
            
            absent = [
                {
                    'student_id': s['student_id'],
                    'name': s['name']
                }
                for s in all_students
                if s['student_id'] not in present_ids
            ]
            
            result = {
                'total_faces_detected': num_faces,
                'recognized_students': len(detected_students),
                'unknown_faces': unknown_faces,
                'present': present,
                'absent': absent,
                'present_count': len(present),
                'absent_count': len(absent),
                'timestamp': datetime.now().isoformat(),
                'recognition_method': 'YOLOv8 + Face Matching'
            }
            
            logger.info(f"📊 Attendance Summary:")
            logger.info(f"   Total faces: {num_faces}")
            logger.info(f"   Recognized: {len(detected_students)}")
            logger.info(f"   Unknown: {unknown_faces}")
            logger.info(f"   Present: {len(present)} students")
            logger.info(f"   Absent: {len(absent)} students")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing attendance: {e}")
            raise
    
    async def rebuild_all_encodings(self, class_name: str = "AIDS") -> Dict:
        """
        Rebuild face encodings for all students in a class
        """
        logger.info("🔄 Rebuilding face encodings...")
        
        # Get all students from the class
        students = await self.student_service.get_students(class_name)
        
        success_count = 0
        failed_count = 0
        
        for student in students:
            student_id = student['student_id']
            
            # Find student's image
            image_dir = f"backend/data/student_images/{student_id}"
            if not os.path.exists(image_dir):
                image_dir = f"data/student_images/{student_id}"
            
            if not os.path.exists(image_dir):
                logger.warning(f"No images found for student {student_id}")
                failed_count += 1
                continue
            
            # Get first image
            images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            if not images:
                logger.warning(f"No image files for student {student_id}")
                failed_count += 1
                continue
            
            image_path = os.path.join(image_dir, images[0])
            
            # Enroll student
            success = await self.enroll_student_faces(student_id, image_path)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        result = {
            'total_students': len(students),
            'success': success_count,
            'failed': failed_count,
            'encodings_file': self.encodings_file
        }
        
        logger.info(f"✅ Encoding rebuild complete:")
        logger.info(f"   Success: {success_count}")
        logger.info(f"   Failed: {failed_count}")
        
        return result


# Global instance
yolov8_attendance_service = None

def get_yolov8_attendance_service(student_service):
    """Get or create YOLOv8 attendance service instance"""
    global yolov8_attendance_service
    if yolov8_attendance_service is None:
        yolov8_attendance_service = YOLOv8AttendanceService(student_service)
    return yolov8_attendance_service
