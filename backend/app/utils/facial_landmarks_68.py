"""
68-Point Facial Landmarks Analysis using dlib
Advanced facial analysis for attendance system
"""

import cv2
import numpy as np
import dlib
from typing import Tuple, Dict, Optional, List
import logging
import os

logger = logging.getLogger(__name__)


class FacialLandmarks68Analyzer:
    """Analyze 68-point facial landmarks using dlib"""
    
    def __init__(self):
        # Pose thresholds
        self.yaw_threshold = 15.0
        self.pitch_threshold = 15.0
        self.roll_threshold = 15.0
        
        # Eye state thresholds
        self.eye_ar_threshold = 0.25  # Below this = closed
        self.eye_ar_consec_frames = 3
        
        # Mouth state thresholds
        self.mouth_ar_threshold = 0.3  # Above this = open
        
        # Initialize dlib detector and predictor
        self._initialize_dlib()
    
    def _initialize_dlib(self):
        """Initialize dlib face detector and shape predictor"""
        try:
            # Face detector
            self.detector = dlib.get_frontal_face_detector()
            
            # Shape predictor (68 landmarks)
            model_path = self._get_model_path()
            
            if not os.path.exists(model_path):
                logger.warning(f"68-point model not found at {model_path}")
                logger.info("Downloading model...")
                self._download_model(model_path)
            
            self.predictor = dlib.shape_predictor(model_path)
            logger.info("dlib 68-point landmark predictor initialized")
            
        except Exception as e:
            logger.error(f"Error initializing dlib: {e}")
            self.detector = None
            self.predictor = None
    
    def _get_model_path(self) -> str:
        """Get path to shape predictor model"""
        if os.path.exists("app/data/models"):
            return "app/data/models/shape_predictor_68_face_landmarks.dat"
        else:
            return "data/models/shape_predictor_68_face_landmarks.dat"
    
    def _download_model(self, output_path: str):
        """Download and extract dlib 68-point model"""
        import urllib.request
        import bz2
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            compressed_path = output_path + ".bz2"
            
            logger.info(f"Downloading from {url}...")
            urllib.request.urlretrieve(url, compressed_path)
            
            logger.info("Extracting model...")
            with bz2.open(compressed_path, "rb") as f:
                with open(output_path, "wb") as out:
                    out.write(f.read())
            
            os.remove(compressed_path)
            logger.info("Model downloaded and extracted successfully")
            
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            raise
    
    def extract_landmarks(self, image: np.ndarray, face_bbox: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """
        Extract 68-point landmarks from face image.
        
        Args:
            image: BGR image
            face_bbox: Optional (x, y, w, h) bounding box
        
        Returns:
            68x2 numpy array of landmark coordinates or None
        """
        try:
            if self.predictor is None:
                logger.error("dlib predictor not initialized")
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect face if bbox not provided
            if face_bbox is None:
                faces = self.detector(gray)
                if len(faces) == 0:
                    logger.warning("No face detected by dlib")
                    return None
                rect = faces[0]
            else:
                # Convert bbox to dlib rectangle
                x, y, w, h = face_bbox
                rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
            
            # Predict landmarks
            shape = self.predictor(gray, rect)
            
            # Convert to numpy array
            landmarks = np.array([[p.x, p.y] for p in shape.parts()])
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Error extracting landmarks: {e}")
            return None
    
    def calculate_yaw(self, landmarks: np.ndarray) -> float:
        """
        Calculate yaw angle using 68-point landmarks.
        
        Formula:
            Uses nose tip (30) and jawline (0, 16)
            More accurate than 5-point
        """
        try:
            nose_tip = landmarks[30]
            left_jaw = landmarks[0]
            right_jaw = landmarks[16]
            
            face_center_x = (left_jaw[0] + right_jaw[0]) / 2
            face_width = right_jaw[0] - left_jaw[0]
            
            nose_offset = nose_tip[0] - face_center_x
            
            yaw = (nose_offset / face_width) * 90
            
            return float(yaw)
            
        except Exception as e:
            logger.error(f"Error calculating yaw: {e}")
            return 0.0
    
    def calculate_pitch(self, landmarks: np.ndarray) -> float:
        """
        Calculate pitch angle using 68-point landmarks.
        
        Formula:
            Uses eye centers (average of 6 points each) and mouth center
        """
        try:
            # Eye centers (average of all eye points)
            left_eye_center = np.mean(landmarks[36:42], axis=0)
            right_eye_center = np.mean(landmarks[42:48], axis=0)
            eye_center = (left_eye_center + right_eye_center) / 2
            
            # Mouth center (average of all mouth points)
            mouth_center = np.mean(landmarks[48:68], axis=0)
            
            vertical_distance = mouth_center[1] - eye_center[1]
            eye_distance = np.linalg.norm(right_eye_center - left_eye_center)
            
            ratio = vertical_distance / eye_distance
            expected_ratio = 1.8  # Calibrated for 68-point
            
            pitch = (ratio - expected_ratio) * 50
            
            return float(pitch)
            
        except Exception as e:
            logger.error(f"Error calculating pitch: {e}")
            return 0.0
    
    def calculate_roll(self, landmarks: np.ndarray) -> float:
        """
        Calculate roll angle using 68-point landmarks.
        
        Formula:
            Uses eye centers (more accurate than single points)
        """
        try:
            left_eye_center = np.mean(landmarks[36:42], axis=0)
            right_eye_center = np.mean(landmarks[42:48], axis=0)
            
            delta_y = right_eye_center[1] - left_eye_center[1]
            delta_x = right_eye_center[0] - left_eye_center[0]
            
            roll = np.degrees(np.arctan2(delta_y, delta_x))
            
            return float(roll)
            
        except Exception as e:
            logger.error(f"Error calculating roll: {e}")
            return 0.0
    
    def calculate_pose_angles(self, landmarks: np.ndarray) -> Tuple[float, float, float]:
        """Calculate all pose angles"""
        yaw = self.calculate_yaw(landmarks)
        pitch = self.calculate_pitch(landmarks)
        roll = self.calculate_roll(landmarks)
        
        return (yaw, pitch, roll)
    
    def calculate_eye_aspect_ratio(self, eye_landmarks: np.ndarray) -> float:
        """
        Calculate Eye Aspect Ratio (EAR).
        
        Formula:
            EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
        
        Args:
            eye_landmarks: 6 points for one eye
        
        Returns:
            EAR value (> 0.25 = open, < 0.20 = closed)
        """
        try:
            # Vertical distances
            A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
            B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
            
            # Horizontal distance
            C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
            
            # EAR
            ear = (A + B) / (2.0 * C)
            
            return float(ear)
            
        except Exception as e:
            logger.error(f"Error calculating EAR: {e}")
            return 0.3  # Default to "open"
    
    def detect_eye_state(self, landmarks: np.ndarray) -> Dict:
        """
        Detect if eyes are open or closed.
        
        Returns:
            {
                'left_eye_open': True/False,
                'right_eye_open': True/False,
                'both_eyes_open': True/False,
                'left_ear': 0.28,
                'right_ear': 0.26
            }
        """
        try:
            left_eye = landmarks[36:42]
            right_eye = landmarks[42:48]
            
            left_ear = self.calculate_eye_aspect_ratio(left_eye)
            right_ear = self.calculate_eye_aspect_ratio(right_eye)
            
            left_open = left_ear > self.eye_ar_threshold
            right_open = right_ear > self.eye_ar_threshold
            
            return {
                'left_eye_open': left_open,
                'right_eye_open': right_open,
                'both_eyes_open': left_open and right_open,
                'left_ear': left_ear,
                'right_ear': right_ear
            }
            
        except Exception as e:
            logger.error(f"Error detecting eye state: {e}")
            return {
                'left_eye_open': True,
                'right_eye_open': True,
                'both_eyes_open': True,
                'left_ear': 0.3,
                'right_ear': 0.3
            }
    
    def calculate_mouth_aspect_ratio(self, landmarks: np.ndarray) -> float:
        """
        Calculate Mouth Aspect Ratio (MAR).
        
        Formula:
            MAR = (||p2-p8|| + ||p3-p7|| + ||p4-p6||) / (3 × ||p1-p5||)
        """
        try:
            mouth = landmarks[48:68]
            
            # Vertical distances
            A = np.linalg.norm(mouth[3] - mouth[9])   # 51-57
            B = np.linalg.norm(mouth[14] - mouth[18]) # 62-66
            C = np.linalg.norm(mouth[15] - mouth[17]) # 63-65
            
            # Horizontal distance
            D = np.linalg.norm(mouth[0] - mouth[6])   # 48-54
            
            # MAR
            mar = (A + B + C) / (3.0 * D)
            
            return float(mar)
            
        except Exception as e:
            logger.error(f"Error calculating MAR: {e}")
            return 0.2  # Default to "closed"
    
    def detect_mouth_state(self, landmarks: np.ndarray) -> Dict:
        """
        Detect mouth state (closed/talking/open).
        
        Returns:
            {
                'state': 'closed' | 'talking' | 'open',
                'mar': 0.25,
                'is_open': False
            }
        """
        try:
            mar = self.calculate_mouth_aspect_ratio(landmarks)
            
            if mar < 0.3:
                state = 'closed'
                is_open = False
            elif mar < 0.6:
                state = 'talking'
                is_open = True
            else:
                state = 'open'
                is_open = True
            
            return {
                'state': state,
                'mar': mar,
                'is_open': is_open
            }
            
        except Exception as e:
            logger.error(f"Error detecting mouth state: {e}")
            return {
                'state': 'closed',
                'mar': 0.2,
                'is_open': False
            }
    
    def detect_occlusion(self, landmarks: np.ndarray) -> Dict:
        """
        Advanced occlusion detection using 68 points.
        
        Detects:
        - Mask (mouth covered)
        - Hand covering face
        - Partial occlusion
        """
        try:
            # Mouth width check (mask detection)
            mouth_width = np.linalg.norm(landmarks[48] - landmarks[54])
            eye_distance = np.linalg.norm(
                np.mean(landmarks[36:42], axis=0) - 
                np.mean(landmarks[42:48], axis=0)
            )
            
            mouth_ratio = mouth_width / eye_distance
            expected_mouth_ratio = 0.65
            
            occluded_regions = []
            
            # Mask detection
            if mouth_ratio < 0.4:
                occluded_regions.append('mouth')
            
            # Nose visibility check
            nose_points = landmarks[27:36]
            nose_width = np.linalg.norm(landmarks[31] - landmarks[35])
            if nose_width < eye_distance * 0.3:
                occluded_regions.append('nose')
            
            # Jawline visibility
            jawline = landmarks[0:17]
            jawline_span = landmarks[16][0] - landmarks[0][0]
            if jawline_span < eye_distance * 2.0:
                occluded_regions.append('jawline')
            
            is_occluded = len(occluded_regions) > 0
            confidence = 1.0 - (len(occluded_regions) * 0.25)
            
            return {
                'is_occluded': is_occluded,
                'occluded_regions': occluded_regions,
                'confidence': max(0.0, confidence),
                'likely_mask': 'mouth' in occluded_regions and 'nose' in occluded_regions
            }
            
        except Exception as e:
            logger.error(f"Error detecting occlusion: {e}")
            return {
                'is_occluded': False,
                'occluded_regions': [],
                'confidence': 1.0,
                'likely_mask': False
            }
    
    def calculate_face_symmetry(self, landmarks: np.ndarray) -> float:
        """
        Calculate face symmetry score.
        
        Returns:
            Symmetry score 0.0-1.0 (1.0 = perfectly symmetric)
        """
        try:
            nose_tip_x = landmarks[30][0]
            
            # Compare left and right jawline
            left_jaw = landmarks[0:9]
            right_jaw = landmarks[16:7:-1]
            
            symmetry_error = 0.0
            
            for left_point, right_point in zip(left_jaw, right_jaw):
                left_dist = abs(left_point[0] - nose_tip_x)
                right_dist = abs(right_point[0] - nose_tip_x)
                symmetry_error += abs(left_dist - right_dist)
            
            face_width = landmarks[16][0] - landmarks[0][0]
            normalized_error = symmetry_error / (len(left_jaw) * face_width)
            
            symmetry_score = max(0.0, 1.0 - normalized_error)
            
            return float(symmetry_score)
            
        except Exception as e:
            logger.error(f"Error calculating symmetry: {e}")
            return 0.8  # Default moderate symmetry
    
    def is_frontal_face(self, landmarks: np.ndarray) -> bool:
        """
        Determine if face is frontal using 68-point landmarks.
        
        More accurate than 5-point version.
        """
        try:
            yaw, pitch, roll = self.calculate_pose_angles(landmarks)
            
            # Also check symmetry
            symmetry = self.calculate_face_symmetry(landmarks)
            
            is_frontal = (
                abs(yaw) <= self.yaw_threshold and
                abs(pitch) <= self.pitch_threshold and
                abs(roll) <= self.roll_threshold and
                symmetry > 0.7  # Additional symmetry check
            )
            
            logger.debug(f"Frontal check: yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}°, symmetry={symmetry:.2f} → {is_frontal}")
            return is_frontal
            
        except Exception as e:
            logger.error(f"Error checking frontal face: {e}")
            return False
    
    def comprehensive_analysis(self, image: np.ndarray, face_bbox: Optional[Tuple] = None) -> Dict:
        """
        Comprehensive facial analysis using all 68-point features.
        
        Returns complete analysis including:
        - Pose angles
        - Eye state
        - Mouth state
        - Occlusion
        - Symmetry
        - Frontal face check
        """
        try:
            landmarks = self.extract_landmarks(image, face_bbox)
            
            if landmarks is None:
                return {
                    'success': False,
                    'error': 'Could not extract landmarks'
                }
            
            pose_angles = self.calculate_pose_angles(landmarks)
            eye_state = self.detect_eye_state(landmarks)
            mouth_state = self.detect_mouth_state(landmarks)
            occlusion = self.detect_occlusion(landmarks)
            symmetry = self.calculate_face_symmetry(landmarks)
            is_frontal = self.is_frontal_face(landmarks)
            
            return {
                'success': True,
                'landmarks': landmarks.tolist(),
                'pose': {
                    'yaw': pose_angles[0],
                    'pitch': pose_angles[1],
                    'roll': pose_angles[2]
                },
                'eyes': eye_state,
                'mouth': mouth_state,
                'occlusion': occlusion,
                'symmetry': symmetry,
                'is_frontal': is_frontal,
                'quality_flags': {
                    'eyes_closed': not eye_state['both_eyes_open'],
                    'mouth_open': mouth_state['is_open'],
                    'occluded': occlusion['is_occluded'],
                    'non_frontal': not is_frontal
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
