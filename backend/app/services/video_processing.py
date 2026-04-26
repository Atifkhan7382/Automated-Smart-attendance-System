"""
Video Processing Service
Handles video frame extraction for student enrollment
"""

import cv2
import os
import json
from typing import List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """Service for processing videos and extracting frames"""
    
    def __init__(self):
        self.settings_file = "data/app_settings.json"
        self.default_settings = {
            "fpsExtraction": 2,
            "similarityThreshold": 0.6,
            "useGPU": False
        }
    
    def load_settings(self) -> dict:
        """Load application settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return self.default_settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self.default_settings
    
    def extract_frames_from_video(self, video_path: str, output_dir: str, student_id: str) -> List[str]:
        """
        Extract frames from video based on saved settings
        
        Args:
            video_path: Path to the input video file
            output_dir: Directory to save extracted frames
            student_id: Student ID for naming files
            
        Returns:
            List of paths to extracted frame images
        """
        try:
            # Load settings
            settings = self.load_settings()
            fps_extraction = settings.get("fpsExtraction", 2)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video properties - FPS: {fps}, Total frames: {total_frames}, Duration: {duration:.2f}s")
            
            # Calculate frame extraction interval
            frame_interval = max(1, int(fps / fps_extraction))
            
            extracted_frames = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified intervals
                if frame_count % frame_interval == 0:
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{student_id}_frame_{extracted_count:03d}_{timestamp}.jpg"
                    frame_path = os.path.join(output_dir, filename)
                    
                    # Save frame
                    success = cv2.imwrite(frame_path, frame)
                    if success:
                        extracted_frames.append(frame_path)
                        extracted_count += 1
                        logger.info(f"Extracted frame {extracted_count}: {filename}")
                    else:
                        logger.error(f"Failed to save frame: {frame_path}")
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"Extraction complete. Total frames extracted: {extracted_count}")
            return extracted_frames
            
        except Exception as e:
            logger.error(f"Error extracting frames from video: {e}")
            raise e
    
    def process_student_video(self, video_path: str, student_id: str, student_name: str, class_name: str) -> dict:
        """
        Process student video and extract frames for training
        
        Args:
            video_path: Path to the uploaded video
            student_id: Student ID
            student_name: Student name
            class_name: Class name
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Create student directory
            student_dir = os.path.join("data/student_images", student_id)
            os.makedirs(student_dir, exist_ok=True)
            
            # Extract frames
            extracted_frames = self.extract_frames_from_video(video_path, student_dir, student_id)
            
            if not extracted_frames:
                raise ValueError("No frames were extracted from the video")
            
            # Process frames (resize, enhance, etc.)
            processed_frames = []
            for frame_path in extracted_frames:
                processed_path = self.process_frame(frame_path)
                processed_frames.append(processed_path)
            
            result = {
                "success": True,
                "student_id": student_id,
                "student_name": student_name,
                "class_name": class_name,
                "video_path": video_path,
                "frames_extracted": len(extracted_frames),
                "frame_paths": processed_frames,
                "student_dir": student_dir
            }
            
            logger.info(f"Video processing completed for student {student_name} ({student_id})")
            return result
            
        except Exception as e:
            logger.error(f"Error processing student video: {e}")
            return {
                "success": False,
                "error": str(e),
                "student_id": student_id,
                "student_name": student_name,
                "class_name": class_name
            }
    
    def process_frame(self, frame_path: str) -> str:
        """
        Process and enhance a single frame
        
        Args:
            frame_path: Path to the frame image
            
        Returns:
            Path to the processed frame
        """
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                raise ValueError(f"Could not load image: {frame_path}")
            
            # Convert to RGB (OpenCV uses BGR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize image to standard size (optional)
            height, width = image_rgb.shape[:2]
            if width > 800 or height > 600:
                # Resize maintaining aspect ratio
                scale = min(800/width, 600/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
            
            # Enhance image quality (optional)
            # You can add more image enhancement here
            
            # Generate processed filename
            base_name = os.path.splitext(frame_path)[0]
            processed_path = f"{base_name}_processed.jpg"
            
            # Convert back to BGR for saving
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
            # Save processed image
            cv2.imwrite(processed_path, image_bgr)
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_path}: {e}")
            return frame_path  # Return original if processing fails
    
    def validate_video(self, video_path: str) -> dict:
        """
        Validate video file and return video properties
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with validation results and video properties
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    "valid": False,
                    "error": "Could not open video file"
                }
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            # Validate video properties
            if duration < 2:  # Minimum 2 seconds
                return {
                    "valid": False,
                    "error": "Video too short. Minimum 2 seconds required."
                }
            
            if duration > 300:  # Maximum 5 minutes
                return {
                    "valid": False,
                    "error": "Video too long. Maximum 5 minutes allowed."
                }
            
            return {
                "valid": True,
                "fps": fps,
                "total_frames": total_frames,
                "width": width,
                "height": height,
                "duration": duration,
                "estimated_frames": int(duration * self.load_settings().get("fpsExtraction", 2))
            }
            
        except Exception as e:
            logger.error(f"Error validating video: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
