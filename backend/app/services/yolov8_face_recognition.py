"""
YOLO-Based Face Recognition Service
High-accuracy face detection and recognition using Ultralytics YOLO and InsightFace (ArcFace)
Enhanced with face quality assessment and 68-point facial landmarks analysis
"""

import cv2
import numpy as np
import os
import pickle
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import torch
from insightface.app import FaceAnalysis
from ultralytics.models.yolo import YOLO
from sklearn.metrics.pairwise import cosine_similarity
import logging


# Import InsightFace
try:
    import insightface  
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("InsightFace not available. Install with: pip install insightface onnxruntime")

from app.services.student_management import StudentManagementService

# Import quality assessment and landmarks analysis utilities
try:
    from app.utils.face_quality import FaceQualityAssessor
    from app.utils.facial_landmarks_68 import FacialLandmarks68Analyzer
    from app.utils.verification_manager import verification_manager
    QUALITY_UTILS_AVAILABLE = True
except ImportError:
    QUALITY_UTILS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Quality utils not available. Face quality assessment disabled.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YOLOv8FaceRecognitionService:
    """Advanced face recognition using Ultralytics YOLO for detection and InsightFace (ArcFace) for recognition"""
    
    def __init__(self):
        self.student_service = StudentManagementService()
        
        # Determine correct path based on working directory
        if os.path.exists("app/data"):
            self.encodings_file = "app/data/encodings/yolov8_face_encodings.pkl"
            self.settings_file = "app/data/app_settings.json"
            self.model_dir = "app/data/models"
        elif os.path.exists("backend/data"):
            self.encodings_file = "backend/data/encodings/yolov8_face_encodings.pkl"
            self.settings_file = "backend/data/app_settings.json"
            self.model_dir = "backend/data/models"
        else:
            self.encodings_file = "data/encodings/yolov8_face_encodings.pkl"
            self.settings_file = "data/app_settings.json"
            self.model_dir = "data/models"
        
        # Create directories
        os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Face encodings storage
        self.known_face_encodings = {}
        self.known_face_names = {}
        
        # YOLO Configuration
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Load YOLO face detection model
        self._initialize_yolo_model()
        
        # InsightFace Configuration
        self.face_recognition_model = 'buffalo_l'  # Options: buffalo_l, buffalo_s, buffalo_sc
        self.distance_metric = 'cosine'  # Options: cosine, euclidean
        
        # Recognition thresholds - UPDATED: Now using 0.60 from settings (balanced for accuracy)
        self.similarity_threshold = 0.25  # Default - will be overridden by settings (0.60)
        self.min_confidence_score = 0.30  # Minimum confidence for detection
        
        # Teacher verification settings
        self.verification_enabled = True
        self.verification_threshold = 0.60
        self.verification_top_candidates = 3
        self.verification_min_quality = 0.80
        self.verification_auto_approve = 0.75
        
        # Initialize InsightFace
        self.face_analyzer = None
        self._initialize_insightface()
        
        # Detection settings
        self.detection_confidence = 0.35  # Confidence threshold (slightly lower to avoid misses)
        self.iou_threshold = 0.45  # Non-maximum suppression threshold
        
        # Initialize quality assessment and landmarks analysis
        self.quality_assessor = None
        self.landmarks_analyzer = None
        self._initialize_quality_utils()
        
        # Load settings
        self._load_settings()
        
        # Caching
        self._class_students_cache = {}
        self._class_encodings_cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_update = {}
    
    def _initialize_yolo_model(self):
        """Initialize Ultralytics YOLO model for face detection.

        Prefers latest YOLOv11 models when available, with graceful fallback to YOLOv8.
        Search order:
        1) yolo11n-face.pt (local)
        2) yolo11n.pt (auto-download by Ultralytics)
        3) yolov8n-face.pt (local)
        4) yolov8n.pt (auto-download)
        """
        try:
            # Prefer YOLOv11 if present/supported
            model_candidates = [
                os.path.join(self.model_dir, 'yolo11n-face.pt'),
                'yolo11n.pt',
                os.path.join(self.model_dir, 'yolov8n-face.pt'),
                'yolov8n.pt',
            ]

            selected_model = None
            for candidate in model_candidates:
                # If candidate is a local path, ensure it exists; if it's a hub id, try it
                if os.path.isabs(candidate) or os.sep in candidate:
                    if os.path.exists(candidate):
                        selected_model = candidate
                        break
                else:
                    # hub id like 'yolo11n.pt' or 'yolov8n.pt'
                    selected_model = candidate
                    break

            # Fallback to default if no model found
            if selected_model is None:
                selected_model = 'yolov8n.pt'

            logger.info(f"Loading YOLO model: {selected_model}")
            self.yolo_model = YOLO(selected_model)
            
            # Move model to device
            self.yolo_model.to(self.device)
            logger.info(f"YOLO model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            logger.info("Falling back to default 'yolov8n.pt' model")
            self.yolo_model = YOLO('yolov8n.pt')
            self.yolo_model.to(self.device)
    
    def _initialize_insightface(self):
        """Initialize InsightFace for face recognition"""
        try:
            if not INSIGHTFACE_AVAILABLE:
                logger.error("InsightFace not available. Please install: pip install insightface onnxruntime")
                return
            
            logger.info("Initializing InsightFace (ArcFace) model...")
            self.face_analyzer = FaceAnalysis(
                name=self.face_recognition_model,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider'] if torch.cuda.is_available() else ['CPUExecutionProvider']
            )
            # Balanced detector input size for speed and accuracy
            self.face_analyzer.prepare(ctx_id=0 if torch.cuda.is_available() else -1, det_size=(640, 640))
            logger.info(f"InsightFace model '{self.face_recognition_model}' loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading InsightFace model: {e}")
            logger.info("Face recognition will not be available")
            self.face_analyzer = None
    
    def _load_settings(self):
        """Load detection and recognition settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # YOLOv8 settings
                    yolo_settings = settings.get('yolov8Detection', {})
                    self.detection_confidence = yolo_settings.get('confidence', 0.50)
                    self.iou_threshold = yolo_settings.get('iouThreshold', 0.45)
                    
                    # Recognition settings
                    # Prefer explicit InsightFace settings if present, otherwise map from legacy keys
                    insightface_settings = settings.get('insightfaceRecognition', {})
                    if insightface_settings:
                        self.face_recognition_model = insightface_settings.get('model', 'buffalo_l')
                        self.distance_metric = insightface_settings.get('distanceMetric', 'cosine')
                        self.similarity_threshold = insightface_settings.get('similarityThreshold', 0.40)
                    else:
                        legacy = settings.get('deepfaceRecognition', {})
                        # Keep using cosine similarity threshold from legacy config
                        self.similarity_threshold = legacy.get('similarityThreshold', 0.40)
                        self.distance_metric = legacy.get('distanceMetric', 'cosine')
                        # Do NOT overwrite InsightFace model name with DeepFace's (e.g., 'Facenet512')
                    # Keep a minimum detection confidence for filtering detections, not recognition
                    self.min_confidence_score = float(settings.get('faceRecognition', {}).get('minConfidence', 0.45))
                    
                    # Teacher verification settings
                    verification_settings = settings.get('teacherVerification', {})
                    self.verification_enabled = verification_settings.get('enabled', True)
                    self.verification_threshold = verification_settings.get('requireVerificationThreshold', 0.60)
                    self.verification_top_candidates = verification_settings.get('showTopCandidates', 3)
                    self.verification_min_quality = verification_settings.get('minQualityForLearning', 0.80)
                    self.verification_auto_approve = verification_settings.get('autoApproveAbove', 0.75)
                    
                    logger.info(f"YOLOv8 Detection Confidence: {self.detection_confidence}")
                    logger.info(f"Recognition Model: {self.face_recognition_model}")
                    logger.info(f"Teacher Verification: {'Enabled' if self.verification_enabled else 'Disabled'}")
                    logger.info(f"Settings loaded from {self.settings_file}")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")
    
    def _initialize_quality_utils(self):
        """Initialize face quality assessment and 68-point landmarks analysis"""
        try:
            if not QUALITY_UTILS_AVAILABLE:
                logger.warning("Quality utils not available. Face quality assessment disabled.")
                return
            
            logger.info("Initializing face quality assessment...")
            self.quality_assessor = FaceQualityAssessor()
            logger.info("Face quality assessor initialized successfully")
            
            logger.info("Initializing 68-point facial landmarks analyzer...")
            self.landmarks_analyzer = FacialLandmarks68Analyzer()
            logger.info("68-point landmarks analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing quality utils: {e}")
            logger.info("Face quality assessment will not be available")
            self.quality_assessor = None
            self.landmarks_analyzer = None
    
    async def load_encodings(self):
        """Load existing face encodings from file (supports both single and multi-encoding format)"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    encodings_data = data.get('encodings', {})
                    self.known_face_names = data.get('names', {})
                    
                    # Convert single encodings to list format for consistency
                    self.known_face_encodings = {}
                    for student_id, encoding in encodings_data.items():
                        if isinstance(encoding, list):
                            # Already multi-encoding format
                            self.known_face_encodings[student_id] = encoding
                        else:
                            # Single encoding - convert to list
                            self.known_face_encodings[student_id] = [encoding]
                    
                logger.info(f"Loaded YOLOv8 encodings for {len(self.known_face_encodings)} students")
            else:
                logger.info("No existing YOLOv8 encodings found. Starting fresh.")
        except Exception as e:
            logger.error(f"Error loading encodings: {e}")
            self.known_face_encodings = {}
            self.known_face_names = {}
    
    async def save_encodings(self):
        """Save face encodings to file"""
        try:
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            with open(self.encodings_file, 'wb') as f:
                pickle.dump({
                    'encodings': self.known_face_encodings,
                    'names': self.known_face_names,
                    'model': self.face_recognition_model,
                    'distance_metric': self.distance_metric
                }, f)
            logger.info("YOLOv8 face encodings saved successfully")
        except Exception as e:
            logger.error(f"Error saving encodings: {e}")
    
    def detect_faces_yolov8(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect faces using InsightFace's built-in detector (more accurate than YOLOv8 for faces)
        
        Returns:
            List of tuples: (top, right, bottom, left, confidence)
        """
        try:
            if self.face_analyzer is None:
                logger.error("InsightFace not initialized, cannot detect faces")
                return []
            
            # Use InsightFace's detector - it's specifically trained for faces
            faces = self.face_analyzer.get(image)
            
            face_locations = []
            
            for face in faces:
                # Get bounding box
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                
                # Convert to our format (top, right, bottom, left)
                top = int(y1)
                right = int(x2)
                bottom = int(y2)
                left = int(x1)
                
                # Get confidence score
                confidence = float(face.det_score)
                
                # Only accept high-confidence detections
                if confidence >= self.detection_confidence:
                    face_locations.append((top, right, bottom, left, confidence))
            
            logger.info(f"InsightFace detected {len(face_locations)} faces")
            return face_locations
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def extract_face_encoding_insightface(self, image: np.ndarray, face_location: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract face encoding using InsightFace (ArcFace)
        
        Args:
            image: Full image
            face_location: Tuple (top, right, bottom, left)
        
        Returns:
            Face embedding vector or None
        """
        try:
            if self.face_analyzer is None:
                logger.error("InsightFace not initialized")
                return None
            
            top, right, bottom, left = face_location
            
            # Extract face region with padding
            height, width = image.shape[:2]
            padding = 10
            top = max(0, top - padding)
            bottom = min(height, bottom + padding)
            left = max(0, left - padding)
            right = min(width, right + padding)
            
            face_image = image[top:bottom, left:right]
            
            # Check if face is large enough
            if face_image.shape[0] < 30 or face_image.shape[1] < 30:
                logger.warning("Face too small for encoding")
                return None
            
            # InsightFace expects BGR format (same as OpenCV)
            # Get face embedding
            faces = self.face_analyzer.get(face_image)
            
            if faces and len(faces) > 0:
                # Get the first detected face's embedding
                embedding = faces[0].embedding
                # Normalize embedding
                embedding = embedding / np.linalg.norm(embedding)
                return embedding
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting face encoding: {e}")
            return None
    
    async def generate_encoding(self, image_path: str, student_id: str, is_video_frame: bool = False) -> Optional[np.ndarray]:
        """
        Generate face encoding for a student image using InsightFace (ArcFace)
        Enhanced with face quality assessment and 68-point landmarks analysis
        
        Args:
            image_path: Path to student image or video frame
            student_id: Student ID
            is_video_frame: If True, apply relaxed quality checks suitable for video frames
        
        Returns:
            Face embedding or None
        """
        try:
            if self.face_analyzer is None:
                logger.error("InsightFace not initialized")
                return None
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return None
            
            # Enhance image quality
            image = self._enhance_image(image)
            
            # Detect faces and get embeddings using InsightFace
            faces = self.face_analyzer.get(image)
            
            if len(faces) == 0:
                logger.warning(f"No faces detected in {image_path}")
                return None
            
            if len(faces) > 1:
                logger.warning(f"Multiple faces detected in {image_path}. Using largest/highest confidence face.")
                # Sort by detection score (confidence) and get best
                faces.sort(key=lambda x: x.det_score, reverse=True)
            
            # Get the best face
            best_face = faces[0]
            confidence = float(best_face.det_score)
            logger.info(f"Face detected with confidence: {confidence:.3f}")
            
            # QUALITY ASSESSMENT (if available)
            if self.quality_assessor is not None:
                # Extract face region for quality assessment
                bbox = best_face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                face_image = image[y1:y2, x1:x2]
                
                # Assess quality
                quality_result = self.quality_assessor.assess_quality(face_image)
                logger.info(f"Quality assessment: {quality_result['overall']:.2f}")
                logger.info(f"  Blur: {quality_result['blur']:.2f}, Brightness: {quality_result['brightness']:.2f}")
                logger.info(f"  Size: {quality_result['size']:.2f}, Contrast: {quality_result['contrast']:.2f}")
                
                # Reject poor quality images
                # Use relaxed threshold for video frames (0.3) vs static images (0.5)
                quality_threshold = 0.3 if is_video_frame else 0.5
                if quality_result['overall'] < quality_threshold:
                    logger.warning(f"❌ Image quality too low ({quality_result['overall']:.2f}, threshold: {quality_threshold})")
                    logger.warning(f"   Recommendation: {quality_result['recommendation']}")
                    if is_video_frame:
                        logger.info("   (Video frame - using relaxed threshold 0.3)")
                    return None
                
                # Warn about moderate quality
                warn_threshold = 0.5 if is_video_frame else 0.7
                if quality_result['overall'] < warn_threshold:
                    logger.warning(f"⚠️  Image quality is moderate ({quality_result['overall']:.2f})")
            
            # 68-POINT LANDMARKS ANALYSIS (if available)
            # SKIP for video frames - too strict, use InsightFace's 5-point landmarks instead
            if self.landmarks_analyzer is not None and not is_video_frame:
                try:
                    # Extract face region
                    bbox = best_face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    face_bbox = (x1, y1, x2 - x1, y2 - y1)
                    
                    # Comprehensive analysis
                    landmarks_result = self.landmarks_analyzer.comprehensive_analysis(image, face_bbox)
                    
                    if landmarks_result['success']:
                        logger.info("68-point landmarks analysis:")
                        logger.info(f"  Pose: yaw={landmarks_result['pose']['yaw']:.1f}°, "
                                  f"pitch={landmarks_result['pose']['pitch']:.1f}°, "
                                  f"roll={landmarks_result['pose']['roll']:.1f}°")
                        logger.info(f"  Eyes open: {landmarks_result['eyes']['both_eyes_open']}")
                        logger.info(f"  Mouth state: {landmarks_result['mouth']['state']}")
                        logger.info(f"  Frontal face: {landmarks_result['is_frontal']}")
                        logger.info(f"  Symmetry: {landmarks_result['symmetry']:.2f}")
                        
                        # Check quality flags
                        quality_flags = landmarks_result['quality_flags']
                        
                        # Reject if eyes are closed (skip for video frames - momentary blinks are normal)
                        if quality_flags['eyes_closed'] and not is_video_frame:
                            logger.warning("❌ Eyes are closed - rejecting image")
                            return None
                        elif quality_flags['eyes_closed'] and is_video_frame:
                            logger.info("ℹ️  Eyes closed detected but allowing for video frame")
                        
                        # Reject if face is not frontal
                        # For video frames, check against relaxed thresholds (30° vs 15°)
                        if is_video_frame:
                            # Relaxed thresholds for video frames
                            yaw = abs(landmarks_result['pose']['yaw'])
                            pitch = abs(landmarks_result['pose']['pitch'])
                            roll = abs(landmarks_result['pose']['roll'])
                            is_too_extreme = yaw > 30 or pitch > 30 or roll > 30
                            
                            if is_too_extreme:
                                logger.warning("❌ Face pose too extreme for video frame - rejecting")
                                logger.warning(f"   Pose angles: yaw={landmarks_result['pose']['yaw']:.1f}°, "
                                             f"pitch={landmarks_result['pose']['pitch']:.1f}°, "
                                             f"roll={landmarks_result['pose']['roll']:.1f}° (threshold: 30°)")
                                return None
                            elif quality_flags['non_frontal']:
                                logger.info(f"ℹ️  Non-frontal face but within video frame tolerance (yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}°)")
                        else:
                            # Strict check for static images
                            if quality_flags['non_frontal']:
                                logger.warning("❌ Face is not frontal - rejecting image")
                                logger.warning(f"   Pose angles: yaw={landmarks_result['pose']['yaw']:.1f}°, "
                                             f"pitch={landmarks_result['pose']['pitch']:.1f}°, "
                                             f"roll={landmarks_result['pose']['roll']:.1f}°")
                                return None
                        
                        # Reject if face is occluded (mask, hand, etc.)
                        if landmarks_result['occlusion']['is_occluded']:
                            logger.warning("❌ Face is occluded - rejecting image")
                            logger.warning(f"   Occluded regions: {landmarks_result['occlusion']['occluded_regions']}")
                            if landmarks_result['occlusion']['likely_mask']:
                                logger.warning("   Likely wearing a mask")
                            return None
                        
                        # Warn if mouth is open (talking/yawning)
                        if quality_flags['mouth_open']:
                            logger.warning(f"⚠️  Mouth is {landmarks_result['mouth']['state']}")
                        
                        logger.info("✅ All quality checks passed")
                    
                except Exception as e:
                    logger.warning(f"Landmarks analysis failed: {e}")
                    # Continue without landmarks analysis
            
            # Get embedding (already computed by InsightFace)
            encoding = best_face.embedding
            
            # Normalize embedding to unit length for cosine similarity
            norm = np.linalg.norm(encoding)
            if norm > 0:
                encoding = encoding / norm
            
            if encoding is not None:
                # Store single encoding per student (not a list - overwrite previous)
                self.known_face_encodings[student_id] = encoding
                
                # Get student info
                student = await self.student_service.get_student_by_id(student_id)
                if student:
                    self.known_face_names[student_id] = student['name']
                
                logger.info(f"✓ Generated high-quality encoding for {student_id}")
                
                # Save encodings
                await self.save_encodings()
                
                return encoding
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating encoding for {student_id}: {e}")
            return None
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better face detection
        Note: Returns BGR format (expected by InsightFace)
        """
        try:
            # Work with BGR format (what InsightFace expects)
            if len(image.shape) != 3 or image.shape[2] != 3:
                return image
            
            # Denoise (works with BGR)
            enhanced = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            
            # CLAHE for better contrast
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Sharpening
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    async def process_attendance_image(self, image_path: str, class_name: str) -> Dict:
        """
        Process classroom image for attendance using InsightFace (ArcFace)
        OPTIMIZED FOR SPEED
        
        Args:
            image_path: Path to classroom image
            class_name: Class name
        
        Returns:
            Dict with present/absent students and detection info
        """
        try:
            if self.face_analyzer is None:
                raise ValueError("InsightFace not initialized")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Quick resize if too large (skip heavy enhancement)
            max_dim = 1920
            if image.shape[0] > max_dim or image.shape[1] > max_dim:
                scale = max_dim / max(image.shape[0], image.shape[1])
                new_size = (int(image.shape[1] * scale), int(image.shape[0] * scale))
                image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
            
            # Detect faces and get embeddings using InsightFace (single pass - NO enhancement!)
            faces = self.face_analyzer.get(image)
            
            logger.info(f"InsightFace detected {len(faces)} faces in attendance image")
            
            if len(faces) == 0:
                # No faces detected
                class_students = await self._get_cached_class_students(class_name)
                return {
                    'present': [],
                    'absent': [{'student_id': s['student_id'], 'name': s['name']} for s in class_students],
                    'total_faces_detected': 0
                }
            
            # Get class encodings
            class_encodings_data = await self._get_class_encodings(class_name)
            all_class_encodings = class_encodings_data['encodings']
            student_id_mapping = class_encodings_data['mapping']
            student_info_cache = class_encodings_data['student_info']
            
            if not all_class_encodings:
                class_students = await self._get_cached_class_students(class_name)
                return {
                    'present': [],
                    'absent': [{'student_id': s['student_id'], 'name': s['name']} for s in class_students],
                    'total_faces_detected': len(faces)
                }
            
            # Process each detected face
            present_students = []
            pending_verifications = []  # Track faces needing verification
            identified_student_ids = set()
            face_locations_for_annotation = []
            attendance_record_id = None  # Will be set when saving attendance
            
            logger.info(f"\n{'='*80}")
            logger.info(f"ATTENDANCE MATCHING - Class: {class_name}")
            logger.info(f"Similarity Threshold: {self.similarity_threshold}")
            logger.info(f"Total Enrolled Students: {len(student_info_cache)}")
            logger.info(f"Students with Encodings: {len(all_class_encodings)}")
            logger.info(f"{'='*80}\n")
            
            for i, face in enumerate(faces):
                # Get embedding (already computed by InsightFace)
                face_encoding = face.embedding
                
                # Normalize
                face_encoding = face_encoding / np.linalg.norm(face_encoding)
                
                # Get bounding box for annotation
                bbox = face.bbox.astype(int)
                detection_conf = float(face.det_score)
                face_locations_for_annotation.append((int(bbox[1]), int(bbox[2]), int(bbox[3]), int(bbox[0]), detection_conf))
                
                if face_encoding is None:
                    logger.warning(f"Could not extract encoding for face {i+1}")
                    continue
                
                logger.info(f"\n--- Face #{i+1} (Detection Confidence: {detection_conf:.3f}) ---")
                
                # QUALITY ASSESSMENT (if available)
                quality_score = 1.0  # Default if quality assessment not available
                if self.quality_assessor is not None:
                    try:
                        # Extract face region
                        x1, y1, x2, y2 = bbox
                        face_image = image[y1:y2, x1:x2]
                        
                        # Assess quality
                        quality_result = self.quality_assessor.assess_quality(face_image)
                        quality_score = quality_result['overall']
                        
                        logger.info(f"Quality: {quality_score:.2f} (blur={quality_result['blur']:.2f}, "
                                  f"brightness={quality_result['brightness']:.2f}, "
                                  f"size={quality_result['size']:.2f})")
                        
                        # Skip very poor quality faces (optional - can be disabled for attendance)
                        # if quality_score < 0.3:
                        #     logger.warning(f"⚠️  Skipping face due to very low quality ({quality_score:.2f})")
                        #     continue
                        
                    except Exception as e:
                        logger.warning(f"Quality assessment failed: {e}")
                        quality_score = 1.0
                
                # Compare with all class encodings
                best_match_student_id = None
                best_similarity = -1
                best_confidence = 0
                
                # Store all similarities for logging
                all_similarities = []
                
                for idx, class_encoding in enumerate(all_class_encodings):
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        face_encoding.reshape(1, -1),
                        class_encoding.reshape(1, -1)
                    )[0][0]
                    
                    student_id = student_id_mapping[idx]
                    student_name = student_info_cache.get(student_id, {}).get('name', 'Unknown')
                    all_similarities.append((student_id, student_name, similarity))
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_student_id = student_id
                        # QUALITY-WEIGHTED CONFIDENCE
                        # Formula: C_final = C_recognition × (0.7 + 0.3 × Q_overall)
                        # This gives 70% weight to recognition, 30% bonus based on quality
                        best_confidence = float(similarity * (0.7 + 0.3 * quality_score))
                
                # Log all similarity scores sorted by score (highest first)
                all_similarities.sort(key=lambda x: x[2], reverse=True)
                logger.info("Similarity scores against all enrolled students:")
                for student_id, student_name, sim_score in all_similarities:
                    status = "✓ MATCH" if sim_score >= self.similarity_threshold else "✗ Below threshold"
                    logger.info(f"  {student_name} (ID: {student_id}): {sim_score:.4f} - {status}")
                
                # Check if match passes similarity threshold only (cosine similarity)
                if best_similarity >= self.similarity_threshold:
                    student_id = best_match_student_id
                    
                    # Avoid duplicates
                    if student_id not in identified_student_ids:
                        student_info = student_info_cache.get(student_id)
                        if student_info:
                            present_students.append({
                                'student_id': student_id,
                                'name': student_info['name'],
                                'confidence': float(best_confidence),  # Quality-weighted confidence
                                'similarity': float(best_similarity),  # Raw similarity score
                                'quality_score': float(quality_score)  # Image quality score
                            })
                            identified_student_ids.add(student_id)
                            logger.info(f"\n✅ IDENTIFIED: {student_info['name']}")
                            logger.info(f"   Similarity: {best_similarity:.4f}")
                            logger.info(f"   Quality Score: {quality_score:.2f}")
                            logger.info(f"   Final Confidence: {best_confidence:.4f}")
                            
                            # CONTINUAL LEARNING: Add encoding from this attendance photo
                            try:
                                # Extract face crop for encoding
                                x1, y1, x2, y2 = bbox
                                face_crop = image[y1:y2, x1:x2]
                                
                                # Add encoding asynchronously (non-blocking)
                                await self.add_encoding_from_attendance(
                                    student_id=student_id,
                                    face_crop=face_crop,
                                    bbox=(x1, y1, x2, y2),
                                    confidence=best_similarity,
                                    quality_score=quality_score
                                )
                            except Exception as e:
                                logger.debug(f"Continual learning update failed (non-critical): {e}")
                    else:
                        logger.info(f"\n⚠️  DUPLICATE: {student_info_cache.get(student_id, {}).get('name', 'Unknown')} already marked present")
                else:
                    logger.warning(f"\n❌ NOT MATCHED: Best similarity {best_similarity:.4f} < threshold {self.similarity_threshold}")
                    if all_similarities:
                        best_student = all_similarities[0]
                        logger.warning(f"   Closest match was: {best_student[1]} with {best_student[2]:.4f}")
                    
                    # TEACHER VERIFICATION: Create verification record if enabled
                    # Create verification only for borderline matches (reduce teacher workload)
                    # Teacher can decide if it's worth identifying or marking as unknown
                    effective_verification_threshold = min(
                        self.verification_threshold,
                        max(self.similarity_threshold - 0.05, 0.0)
                    )
                    if (
                        self.verification_enabled
                        and best_similarity < self.similarity_threshold
                        and best_similarity >= effective_verification_threshold
                    ):
                        try:
                            # Extract face crop
                            x1, y1, x2, y2 = bbox
                            face_crop = image[y1:y2, x1:x2]
                            
                            # Get top N candidates
                            top_candidates = all_similarities[:self.verification_top_candidates]
                            candidates_data = [
                                {
                                    'student_id': student_id,
                                    'name': name,
                                    'similarity': float(sim)
                                }
                                for student_id, name, sim in top_candidates
                            ]
                            
                            # Store for later (will be saved after attendance record is created)
                            pending_verifications.append({
                                'face_index': i,
                                'face_crop': face_crop,
                                'bbox': bbox,
                                'quality_score': quality_score,
                                'candidates': candidates_data,
                                'suggested_student_id': top_candidates[0][0] if top_candidates else None,
                                'suggested_similarity': float(top_candidates[0][2]) if top_candidates else 0.0
                            })
                            
                            logger.info(f"📋 Created verification record for face #{i+1}")
                            logger.info(f"   Best match: {candidates_data[0]['name']} ({candidates_data[0]['similarity']:.4f})")
                            logger.info(f"   Top candidates: {[c['name'] for c in candidates_data]}")
                            
                        except Exception as e:
                            logger.error(f"Failed to create verification record: {e}")
                    else:
                        logger.info(
                            f"Skipped verification: similarity {best_similarity:.4f} below effective threshold "
                            f"{effective_verification_threshold:.4f}"
                        )

            
            # Get absent students
            all_class_students = await self._get_cached_class_students(class_name)
            absent_students = []
            
            for student in all_class_students:
                if student['student_id'] not in identified_student_ids:
                    absent_students.append({
                        'student_id': student['student_id'],
                        'name': student['name']
                    })
            
            # Log summary
            logger.info(f"\n{'='*80}")
            logger.info(f"ATTENDANCE SUMMARY")
            logger.info(f"Total Faces Detected: {len(faces)}")
            logger.info(f"Students Identified: {len(present_students)}")
            logger.info(f"Students Absent: {len(absent_students)}")
            logger.info(f"Pending Verifications: {len(pending_verifications)}")
            logger.info(f"Present: {[s['name'] for s in present_students]}")
            logger.info(f"Absent: {[s['name'] for s in absent_students]}")
            logger.info(f"{'='*80}\n")
            
            # Save annotated image
            await self._save_annotated_image(image_path, image, face_locations_for_annotation, present_students)
            
            return {
                'present': present_students,
                'absent': absent_students,
                'total_faces_detected': len(faces),
                'pending_verifications': pending_verifications,
                'has_pending_verifications': len(pending_verifications) > 0
            }
            
        except Exception as e:
            logger.error(f"Error processing attendance image: {e}")
            raise e
    
    async def _get_cached_class_students(self, class_name: str) -> List[Dict]:
        """Get class students with caching"""
        current_time = datetime.now().timestamp()
        
        if (class_name in self._class_students_cache and 
            class_name in self._last_cache_update and
            current_time - self._last_cache_update[class_name] < self._cache_ttl):
            return self._class_students_cache[class_name]
        
        # Use get_enrolled_students to get students by enrollment table, not class_name field
        students = await self.student_service.get_enrolled_students(class_name)
        self._class_students_cache[class_name] = students
        self._last_cache_update[class_name] = current_time
        
        return students
    
    async def _get_class_encodings(self, class_name: str) -> Dict:
        """Get class encodings with caching"""
        current_time = datetime.now().timestamp()
        
        if (class_name in self._class_encodings_cache and 
            class_name in self._last_cache_update and
            current_time - self._last_cache_update[class_name] < self._cache_ttl):
            return self._class_encodings_cache[class_name]
        
        class_students = await self._get_cached_class_students(class_name)
        
        all_class_encodings = []
        student_id_mapping = []
        student_info_cache = {}
        
        for student in class_students:
            student_id = student['student_id']
            student_info_cache[student_id] = {
                'name': student['name'],
                'class_name': student['class_name']
            }
            
            if student_id in self.known_face_encodings:
                student_encodings = self.known_face_encodings[student_id]
                if isinstance(student_encodings, list):
                    all_class_encodings.extend(student_encodings)
                    student_id_mapping.extend([student_id] * len(student_encodings))
                else:
                    all_class_encodings.append(student_encodings)
                    student_id_mapping.append(student_id)
        
        result = {
            'encodings': all_class_encodings,
            'mapping': student_id_mapping,
            'student_info': student_info_cache
        }
        
        self._class_encodings_cache[class_name] = result
        self._last_cache_update[class_name] = current_time
        
        return result
    
    async def _save_annotated_image(self, original_path: str, image: np.ndarray, 
                                   face_detections: List, identified_students: List):
        """Save annotated image with face boxes"""
        try:
            annotated_image = image.copy()
            
            for i, (top, right, bottom, left, conf) in enumerate(face_detections):
                # Draw rectangle
                cv2.rectangle(annotated_image, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Add label
                if i < len(identified_students):
                    student = identified_students[i]
                    label = f"{student['name']} ({student['confidence']:.2f})"
                    cv2.putText(annotated_image, label, (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.putText(annotated_image, "Unknown", (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Save
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            annotated_dir = "data/attendance_images" if not os.path.exists("app/data") else "app/data/attendance_images"
            os.makedirs(annotated_dir, exist_ok=True)
            annotated_path = os.path.join(annotated_dir, f"annotated_{base_name}.jpg")
            
            # Convert RGB back to BGR for saving
            annotated_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(annotated_path, annotated_bgr)
            
            logger.info(f"Saved annotated image: {annotated_path}")
            
        except Exception as e:
            logger.error(f"Error saving annotated image: {e}")
    
    async def clear_all_encodings(self) -> bool:
        """Clear all face encodings"""
        try:
            self.known_face_encodings = {}
            self.known_face_names = {}
            
            if os.path.exists(self.encodings_file):
                os.remove(self.encodings_file)
            
            logger.info("Cleared all YOLOv8 face encodings")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing encodings: {e}")
            return False
    
    async def remove_encoding(self, student_id: str):
        """Remove a student's face encoding"""
        try:
            if student_id in self.known_face_encodings:
                del self.known_face_encodings[student_id]
            if student_id in self.known_face_names:
                del self.known_face_names[student_id]
            
            await self.save_encodings()
            logger.info(f"Removed encoding for student {student_id}")
        except Exception as e:
            logger.error(f"Error removing encoding: {e}")
    
    def _get_continual_learning_settings(self) -> Dict:
        """Get continual learning settings from app_settings.json"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('continualLearning', {
                        'enabled': True,
                        'minConfidenceThreshold': 0.75,
                        'minQualityThreshold': 0.8,
                        'maxEncodingsPerStudent': 10,
                        'saveFaceCrops': True,
                        'logEncodingAdditions': True,
                        'strictMode': True,
                        'minEncodingConsistency': 0.7
                    })
            return {'enabled': False}
        except Exception as e:
            logger.error(f"Error loading continual learning settings: {e}")
            return {'enabled': False}
    
    async def _assess_encoding_quality(self, encoding: np.ndarray, student_id: str) -> float:
        """
        Assess quality of new encoding against existing ones
        
        Args:
            encoding: New encoding to assess
            student_id: Student ID
        
        Returns:
            Quality score (0-1), higher is better
        """
        try:
            if student_id not in self.known_face_encodings:
                return 1.0  # First encoding, accept it
            
            existing_encodings = self.known_face_encodings[student_id]
            if not isinstance(existing_encodings, list):
                existing_encodings = [existing_encodings]
            
            if len(existing_encodings) == 0:
                return 1.0
            
            # Calculate similarity with existing encodings
            similarities = []
            for existing in existing_encodings:
                # Cosine similarity
                similarity = np.dot(encoding, existing)
                similarities.append(similarity)
            
            # Average similarity - high similarity means consistent with existing
            avg_similarity = np.mean(similarities)
            return float(avg_similarity)
            
        except Exception as e:
            logger.error(f"Error assessing encoding quality: {e}")
            return 0.5
    
    async def add_encoding_from_attendance(
        self,
        student_id: str,
        face_crop: np.ndarray,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        quality_score: float,
        force: bool = False
    ) -> bool:
        """
        Add encoding from attendance photo to improve recognition over time
        
        Args:
            student_id: Student ID
            face_crop: Cropped face image
            bbox: Bounding box (x1, y1, x2, y2)
            confidence: Match confidence
            quality_score: Face quality score
        
        Returns:
            True if encoding was added
        """
        try:
            settings = self._get_continual_learning_settings()

            if not settings.get('enabled', False) and not force:
                return False
            
            # Check thresholds
            if not force:
                if confidence < settings.get('minConfidenceThreshold', 0.6):
                    return False
                
                if quality_score < settings.get('minQualityThreshold', 0.7):
                    return False
            else:
                # Teacher-verified faces: skip confidence gate, keep quality gate
                min_quality = max(settings.get('minQualityThreshold', 0.7), self.verification_min_quality)
                if quality_score < min_quality:
                    return False
            
            # Generate encoding from face crop using InsightFace
            if self.face_analyzer is None:
                return False
            
            # Detect face in crop
            faces = self.face_analyzer.get(face_crop)
            if len(faces) == 0:
                return False
            
            # Get encoding
            new_encoding = faces[0].embedding
            
            # Normalize
            norm = np.linalg.norm(new_encoding)
            if norm > 0:
                new_encoding = new_encoding / norm
            
            # Assess quality
            encoding_quality = await self._assess_encoding_quality(new_encoding, student_id)
            
            # Use stricter consistency threshold in strict mode
            min_consistency = settings.get('minEncodingConsistency', 0.7) if settings.get('strictMode', True) else 0.5
            
            if encoding_quality < min_consistency:
                logger.info(f"🚫 Rejected encoding for {student_id}: consistency {encoding_quality:.3f} < {min_consistency:.3f} (strict mode)")
                return False
            
            # Ensure encodings are loaded before appending
            if not self.known_face_encodings and os.path.exists(self.encodings_file):
                await self.load_encodings()

            # Add to collection
            if student_id not in self.known_face_encodings:
                self.known_face_encodings[student_id] = []
            
            encodings = self.known_face_encodings[student_id]
            if not isinstance(encodings, list):
                encodings = [encodings]
                self.known_face_encodings[student_id] = encodings
            
            # Check limit
            max_encodings = settings.get('maxEncodingsPerStudent', 10)
            if len(encodings) >= max_encodings:
                encodings.pop(0)
            
            encodings.append(new_encoding)
            
            # Save
            await self.save_encodings()
            
            # Log
            if settings.get('logEncodingAdditions', True):
                logger.info(f"📚 Added encoding from attendance for {student_id} (total: {len(encodings)}, quality: {encoding_quality:.3f})")
            
            # Clear cache to reload with new encoding
            self.clear_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding encoding from attendance: {e}")
            return False
    
    def clear_cache(self):
        """Clear all caches"""
        self._class_students_cache.clear()
        self._class_encodings_cache.clear()
        self._last_cache_update.clear()
        logger.info("YOLOv8 face recognition cache cleared")
    
    async def get_recognition_stats(self) -> Dict:
        """Get face recognition statistics"""
        return {
            'total_students_enrolled': len(self.known_face_encodings),
            'recognition_model': self.face_recognition_model,
            'distance_metric': self.distance_metric,
            'similarity_threshold': self.similarity_threshold,
            'detection_confidence': self.detection_confidence,
            'device': self.device,
            'encodings_file_size': os.path.getsize(self.encodings_file) if os.path.exists(self.encodings_file) else 0
        }


# Global instance
yolov8_face_service = YOLOv8FaceRecognitionService()

