"""
Optimized Attendance Processing Service
High-performance attendance marking with caching and batch operations
"""

import asyncio
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import numpy as np
import cv2

# Try to import face_recognition (optional for cloud deployment)
try:
    from app.utils import face_recognition_wrapper as face_recognition
    FACE_RECOGNITION_AVAILABLE = face_recognition.AVAILABLE
except ImportError:
    face_recognition = None  # type: ignore
    FACE_RECOGNITION_AVAILABLE = False

if not FACE_RECOGNITION_AVAILABLE:
    print("⚠️ face_recognition not available in optimized_attendance")

from concurrent.futures import ThreadPoolExecutor
import threading

from app.services.attendance import AttendanceService
from app.services.face_recognition import FaceRecognitionService
from app.services.student_management import StudentManagementService
from app.models.database import DatabaseManager


class OptimizedAttendanceProcessor:
    """High-performance attendance processing with optimizations"""
    
    def __init__(self):
        self.attendance_service = AttendanceService()
        self.face_service = FaceRecognitionService()
        self.student_service = StudentManagementService()
        self.db = DatabaseManager()
        
        # Performance optimizations
        self._processing_cache = {}
        self._cache_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance metrics
        self._metrics = {
            'total_processed': 0,
            'avg_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def process_attendance_optimized(self, image_path: str, class_name: str) -> Dict:
        """Optimized attendance processing with performance tracking"""
        start_time = time.time()
        
        try:
            # OPTIMIZATION 1: Check cache first
            cache_key = f"{class_name}_{hash(image_path)}"
            with self._cache_lock:
                if cache_key in self._processing_cache:
                    self._metrics['cache_hits'] += 1
                    print(f"Cache hit for {class_name}")
                    return self._processing_cache[cache_key]
                self._metrics['cache_misses'] += 1
            
            # OPTIMIZATION 2: Parallel image processing
            image_task = asyncio.create_task(self._load_and_enhance_image(image_path))
            class_data_task = asyncio.create_task(self._get_class_data_optimized(class_name))
            
            # Wait for both tasks
            enhanced_image, class_data = await asyncio.gather(image_task, class_data_task)
            
            # OPTIMIZATION 3: Fast face detection
            face_locations = await self._detect_faces_fast(enhanced_image)
            
            if len(face_locations) == 0:
                result = {
                    'present': [],
                    'absent': class_data['students'],
                    'total_faces_detected': 0,
                    'processing_time': time.time() - start_time
                }
            else:
                # OPTIMIZATION 4: Batch face recognition
                result = await self._batch_face_recognition(
                    enhanced_image, face_locations, class_data
                )
                result['processing_time'] = time.time() - start_time
            
            # OPTIMIZATION 5: Cache result
            with self._cache_lock:
                self._processing_cache[cache_key] = result
                # Limit cache size
                if len(self._processing_cache) > 100:
                    # Remove oldest entries
                    oldest_key = next(iter(self._processing_cache))
                    del self._processing_cache[oldest_key]
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
            return result
            
        except Exception as e:
            print(f"Error in optimized attendance processing: {e}")
            raise e
    
    async def _load_and_enhance_image(self, image_path: str) -> np.ndarray:
        """Load and enhance image with optimizations"""
        def load_image():
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Smart enhancement based on image size
            height, width = image.shape[:2]
            image_size = height * width
            
            if image_size > 1000000:  # 1MP+
                # Use GPU enhancement for large images
                return self.face_service.enhance_image_quality(image)
            else:
                # Simple RGB conversion for small images
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, load_image)
    
    async def _get_class_data_optimized(self, class_name: str) -> Dict:
        """Get class data with caching"""
        # Use face service caching
        students = await self.face_service._get_cached_class_students(class_name)
        encodings_data = await self.face_service._get_class_encodings(class_name)
        
        return {
            'students': students,
            'encodings': encodings_data['encodings'],
            'mapping': encodings_data['mapping'],
            'student_info': encodings_data['student_info']
        }
    
    async def _detect_faces_fast(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Optimized face detection for long-distance classroom scenarios"""
        def detect_faces():
            # Use the improved long-distance detection from face service
            height, width = image.shape[:2]
            image_size = height * width
            return self.face_service._detect_faces_long_distance(image, image_size)
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, detect_faces)
    
    async def _batch_face_recognition(self, image: np.ndarray, face_locations: List, 
                                    class_data: Dict) -> Dict:
        """Batch face recognition for multiple faces"""
        def process_faces():
            # Get face encodings using configurable settings from face service
            face_encodings = face_recognition.face_encodings(
                image,
                face_locations,
                num_jitters=self.face_service.num_jitters,  # Use configured jitters
                model='large'  # Large model for better accuracy
            )
            
            # Batch comparison with improved accuracy
            present_students = []
            identified_student_ids = set()
            
            # Get recognition settings from face service
            tolerance = self.face_service.face_recognition_tolerance
            min_confidence = self.face_service.min_confidence_threshold
            strict_mode = self.face_service.strict_mode
            
            for face_encoding in face_encodings:
                if not class_data['encodings']:
                    continue
                
                # Vectorized distance calculation
                face_distances = face_recognition.face_distance(
                    class_data['encodings'],
                    face_encoding
                )
                
                # Find best match with improved accuracy
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    best_distance = face_distances[best_match_index]
                    confidence = float(1 - best_distance)
                    
                    # Apply same strict matching as main service
                    is_valid_match = False
                    
                    if strict_mode:
                        is_valid_match = (
                            best_distance < tolerance and 
                            confidence >= min_confidence
                        )
                    else:
                        is_valid_match = (
                            best_distance < tolerance or 
                            confidence >= min_confidence
                        )
                    
                    # Check for ambiguous matches (only if enabled)
                    if is_valid_match and self.face_service.use_ambiguous_detection and len(face_distances) > 1:
                        sorted_indices = np.argsort(face_distances)
                        second_best_distance = face_distances[sorted_indices[1]]
                        distance_gap = second_best_distance - best_distance
                        
                        if distance_gap < 0.08:
                            is_valid_match = False
                    
                    if is_valid_match:
                        student_id = class_data['mapping'][best_match_index]
                        
                        if student_id not in identified_student_ids:
                            student_info = class_data['student_info'].get(student_id)
                            if student_info:
                                present_students.append({
                                    'student_id': student_id,
                                    'name': student_info['name'],
                                    'confidence': float(confidence)  # Convert numpy.float32 to Python float
                                })
                                identified_student_ids.add(student_id)
            
            # Get absent students
            absent_students = []
            for student in class_data['students']:
                if student['student_id'] not in identified_student_ids:
                    absent_students.append({
                        'student_id': student['student_id'],
                        'name': student['name']
                    })
            
            return {
                'present': present_students,
                'absent': absent_students,
                'total_faces_detected': len(face_locations)
            }
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, process_faces)
    
    async def save_attendance_optimized(self, class_name: str, image_path: str, 
                                       present_students: List[Dict], 
                                       absent_students: List[Dict], 
                                       total_faces_detected: int) -> int:
        """Optimized attendance saving with batch operations"""
        try:
            # Use optimized attendance service
            attendance_id = await self.attendance_service.save_attendance(
                class_name, image_path, present_students, absent_students, total_faces_detected
            )
            
            # Clear cache for this class to ensure fresh data
            self._clear_class_cache(class_name)
            
            return attendance_id
            
        except Exception as e:
            print(f"Error saving optimized attendance: {e}")
            raise e
    
    def _clear_class_cache(self, class_name: str):
        """Clear cache for specific class"""
        with self._cache_lock:
            keys_to_remove = [key for key in self._processing_cache.keys() 
                            if key.startswith(f"{class_name}_")]
            for key in keys_to_remove:
                del self._processing_cache[key]
    
    def _update_metrics(self, processing_time: float):
        """Update performance metrics"""
        self._metrics['total_processed'] += 1
        
        # Update average processing time
        total = self._metrics['total_processed']
        current_avg = self._metrics['avg_processing_time']
        self._metrics['avg_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        cache_hit_rate = 0
        if self._metrics['cache_hits'] + self._metrics['cache_misses'] > 0:
            cache_hit_rate = (
                self._metrics['cache_hits'] / 
                (self._metrics['cache_hits'] + self._metrics['cache_misses'])
            ) * 100
        
        return {
            'total_processed': self._metrics['total_processed'],
            'avg_processing_time': round(self._metrics['avg_processing_time'], 3),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self._processing_cache),
            'cache_hits': self._metrics['cache_hits'],
            'cache_misses': self._metrics['cache_misses']
        }
    
    def clear_all_caches(self):
        """Clear all caches"""
        with self._cache_lock:
            self._processing_cache.clear()
        
        # Clear face recognition cache
        self.face_service.clear_cache()
        
        print("All caches cleared")
    
    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)


# Global optimized processor instance
optimized_processor = OptimizedAttendanceProcessor()
