"""
Face Quality Assessment Module
Evaluates image quality for face recognition using multiple metrics
"""

import cv2
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class FaceQualityAssessor:
    """Assess face image quality using multiple metrics"""
    
    def __init__(self):
        # Thresholds
        self.min_blur_score = 100
        self.optimal_brightness = 128
        self.min_face_size = 112
        self.min_contrast = 40
        
        # Weights for combined score
        self.weights = {
            'blur': 0.35,
            'brightness': 0.25,
            'size': 0.30,
            'contrast': 0.10
        }
    
    def assess_blur(self, face_image: np.ndarray) -> float:
        """
        Detect image blur using Laplacian variance.
        
        Formula:
            Blur_Score = Var(∇²I)
            Normalized = min(Blur_Score / 500, 1.0)
        
        Args:
            face_image: BGR face image
        
        Returns:
            Normalized blur score (0.0-1.0, higher is sharper)
        """
        try:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            blur_score = laplacian.var()
            
            # Normalize: 500+ is very sharp
            normalized = min(blur_score / 500.0, 1.0)
            
            logger.debug(f"Blur score: {blur_score:.2f} → normalized: {normalized:.2f}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error assessing blur: {e}")
            return 0.0
    
    def assess_brightness(self, face_image: np.ndarray) -> float:
        """
        Evaluate image brightness/exposure.
        
        Formula:
            Brightness = mean(pixel_values)
            Deviation = |Brightness - 128| / 128
            Score = 1.0 - Deviation
        
        Args:
            face_image: BGR face image
        
        Returns:
            Normalized brightness score (0.0-1.0, 1.0 is optimal)
        """
        try:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Optimal brightness is 128 (middle gray)
            deviation = abs(brightness - self.optimal_brightness) / self.optimal_brightness
            score = max(0.0, 1.0 - deviation)
            
            logger.debug(f"Brightness: {brightness:.2f} → score: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"Error assessing brightness: {e}")
            return 0.0
    
    def assess_size(self, face_image: np.ndarray) -> float:
        """
        Check if face is large enough for recognition.
        
        Formula:
            min_dim = min(height, width)
            Score = min(min_dim / 112, 1.0)
        
        Args:
            face_image: BGR face image
        
        Returns:
            Normalized size score (0.0-1.0, 1.0 is optimal)
        """
        try:
            height, width = face_image.shape[:2]
            min_dimension = min(height, width)
            
            # InsightFace works best with 112x112 or larger
            score = min(min_dimension / self.min_face_size, 1.0)
            
            logger.debug(f"Face size: {width}x{height} → score: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"Error assessing size: {e}")
            return 0.0
    
    def assess_contrast(self, face_image: np.ndarray) -> float:
        """
        Measure image contrast using standard deviation.
        
        Formula:
            Contrast = σ(pixel_values)
            Normalized = min(Contrast / 60, 1.0)
        
        Args:
            face_image: BGR face image
        
        Returns:
            Normalized contrast score (0.0-1.0, higher is better)
        """
        try:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            contrast = np.std(gray)
            
            # Normalize: 60+ is good contrast
            normalized = min(contrast / 60.0, 1.0)
            
            logger.debug(f"Contrast: {contrast:.2f} → normalized: {normalized:.2f}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error assessing contrast: {e}")
            return 0.0
    
    def assess_quality(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Comprehensive quality assessment.
        
        Formula:
            Q_overall = Σ(wᵢ × Qᵢ)
            where wᵢ are weights and Qᵢ are individual scores
        
        Args:
            face_image: BGR face image
        
        Returns:
            Dictionary with quality metrics and recommendation
        """
        try:
            # Calculate individual scores
            scores = {
                'blur': self.assess_blur(face_image),
                'brightness': self.assess_brightness(face_image),
                'size': self.assess_size(face_image),
                'contrast': self.assess_contrast(face_image)
            }
            
            # Weighted average
            overall = sum(scores[k] * self.weights[k] for k in scores)
            
            # Recommendation
            if overall >= 0.7:
                recommendation = 'accept'
            elif overall >= 0.5:
                recommendation = 'warning'
            else:
                recommendation = 'reject'
            
            result = {
                'overall': overall,
                **scores,
                'recommendation': recommendation
            }
            
            logger.info(f"Quality assessment: {overall:.2f} ({recommendation})")
            return result
            
        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            return {
                'overall': 0.0,
                'blur': 0.0,
                'brightness': 0.0,
                'size': 0.0,
                'contrast': 0.0,
                'recommendation': 'reject'
            }
