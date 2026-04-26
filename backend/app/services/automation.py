"""
Automated Attendance Service
Handles scheduled automatic attendance marking using camera feed
Enhanced with quality-based retry mechanism and WebSocket notifications
"""

import asyncio
import cv2
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import threading
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, face_service, attendance_service, websocket_manager=None):
        self.face_service = face_service
        self.attendance_service = attendance_service
        self.websocket_manager = websocket_manager  # For real-time notifications
        self.is_running = False
        self.settings = {
            "enabled": False,
            "interval_minutes": 30,
            "class_name": "",
            "camera_source": "0",
            "quality_retry": {
                "enabled": True,
                "max_attempts": 5,
                "wait_seconds": 3,
                "min_quality_threshold": 0.7
            }
        }
        self._default_settings = json.loads(json.dumps(self.settings))
        self.status = {
            "is_running": False,
            "last_run": None,
            "next_run": None,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "retry_stats": {
                "total_retries": 0,
                "quality_failures": 0,
                "max_retries_reached": 0
            }
        }
        self.task = None
        self.lock = threading.Lock()
        self.settings_file = "data/automation_settings.json"
        self.status_file = "data/automation_status.json"
        self._load_settings()
        self._load_status()

    def _load_settings(self):
        """Load automation settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                self._apply_settings_defaults(loaded_settings)
        except Exception as e:
            logger.error(f"Error loading automation settings: {e}")

    def _apply_settings_defaults(self, loaded_settings: Dict[str, Any]):
        """Merge loaded settings with defaults to avoid missing keys"""
        merged = json.loads(json.dumps(self._default_settings))
        if isinstance(loaded_settings, dict):
            merged.update({k: v for k, v in loaded_settings.items() if k != 'quality_retry'})
            quality_retry = loaded_settings.get('quality_retry', {})
            if isinstance(quality_retry, dict):
                merged['quality_retry'].update(quality_retry)
        self.settings = merged

    def _save_settings(self):
        """Save automation settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving automation settings: {e}")

    def _load_status(self):
        """Load automation status from file"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
                # Synchronize is_running flag with loaded status
                self.is_running = self.status.get('is_running', False)
        except Exception as e:
            logger.error(f"Error loading automation status: {e}")

    def _save_status(self):
        """Save automation status to file"""
        try:
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            with open(self.status_file, 'w') as f:
                json.dump(self.status, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving automation status: {e}")

    async def get_settings(self) -> Dict[str, Any]:
        """Get current automation settings"""
        return self.settings.copy()

    async def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation settings"""
        with self.lock:
            self._apply_settings_defaults({**self.settings, **new_settings})
            self._save_settings()
        return self.settings.copy()

    async def get_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return self.status.copy()

    async def capture_from_camera(self, camera_source: str) -> Optional[str]:
        """Capture image from camera"""
        try:
            # Try to parse as integer (camera index) or use as string (RTSP URL)
            try:
                source = int(camera_source)
            except ValueError:
                source = camera_source

            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                logger.error(f"Failed to open camera source: {camera_source}")
                return None

            # Read frame
            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error("Failed to capture frame from camera")
                return None

            # Save frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auto_attendance_{self.settings['class_name']}_{timestamp}.jpg"
            filepath = f"data/attendance_images/{filename}"
            
            os.makedirs("data/attendance_images", exist_ok=True)
            cv2.imwrite(filepath, frame)
            
            logger.info(f"Captured image saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error capturing from camera: {e}")
            return None
    
    async def send_websocket_notification(self, event_type: str, data: Dict[str, Any]):
        """Send WebSocket notification to connected clients"""
        if self.websocket_manager:
            try:
                await self.websocket_manager.broadcast({
                    "type": event_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {e}")
    
    async def assess_image_quality(self, image_path: str) -> Dict[str, Any]:
        """Assess quality of captured image using quality assessor"""
        try:
            # Check if quality assessor is available
            if not hasattr(self.face_service, 'quality_assessor') or self.face_service.quality_assessor is None:
                logger.warning("Quality assessor not available, skipping quality check")
                return {"overall": 1.0, "passed": True, "issues": []}
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"overall": 0.0, "passed": False, "issues": ["Failed to load image"]}
            
            # Detect faces first
            faces = self.face_service.face_analyzer.get(image)
            if len(faces) == 0:
                return {"overall": 0.0, "passed": False, "issues": ["No faces detected"]}
            
            # Get best face
            best_face = max(faces, key=lambda f: f.det_score)
            bbox = best_face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            face_image = image[y1:y2, x1:x2]
            
            # Assess quality
            quality_result = self.face_service.quality_assessor.assess_quality(face_image)
            
            # Determine if quality passes threshold
            min_threshold = self.settings['quality_retry']['min_quality_threshold']
            passed = quality_result['overall'] >= min_threshold
            
            # Identify issues
            issues = []
            if quality_result['blur'] < 0.5:
                issues.append("Image is blurry")
            if quality_result['brightness'] < 0.5:
                issues.append("Poor lighting")
            if quality_result['size'] < 0.5:
                issues.append("Face too small")
            if quality_result['contrast'] < 0.5:
                issues.append("Low contrast")
            
            return {
                "overall": quality_result['overall'],
                "passed": passed,
                "issues": issues,
                "details": quality_result
            }
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return {"overall": 0.0, "passed": False, "issues": [str(e)]}

    async def run_attendance_cycle(self):
        """Run one cycle of automated attendance marking with quality-based retry"""
        try:
            logger.info(f"Starting automated attendance for class: {self.settings['class_name']}")
            
            # Quality retry settings
            retry_enabled = self.settings['quality_retry']['enabled']
            max_attempts = self.settings['quality_retry']['max_attempts'] if retry_enabled else 1
            wait_seconds = self.settings['quality_retry']['wait_seconds']
            
            image_path = None
            quality_passed = False
            attempt = 0
            
            # RETRY LOOP
            while attempt < max_attempts and not quality_passed:
                attempt += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Attempt {attempt}/{max_attempts} to capture a quality image...")
                
                # Capture image from camera
                current_image_path = await self.capture_from_camera(self.settings['camera_source'])
                
                if not current_image_path:
                    logger.error(f"Failed to capture image on attempt {attempt}.")
                    await self.send_websocket_notification("automation_status", {
                        "message": f"Failed to capture image on attempt {attempt}",
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "status": "failed_capture"
                    })
                    if attempt == max_attempts:
                        raise Exception("Failed to capture image from camera after multiple attempts")
                    else:
                        await asyncio.sleep(wait_seconds)
                        continue

                # Assess image quality
                quality_result = await self.assess_image_quality(current_image_path)
                quality_passed = quality_result['passed']
                
                logger.info(f"Image quality assessment (Attempt {attempt}): Overall={quality_result['overall']:.2f}, Passed={quality_passed}")
                if not quality_passed:
                    logger.warning(f"Image quality issues: {', '.join(quality_result['issues'])}")
                    with self.lock:
                        self.status['retry_stats']['total_retries'] += 1
                        self.status['retry_stats']['quality_failures'] += 1
                        self._save_status()
                    
                    await self.send_websocket_notification("automation_status", {
                        "message": f"Image quality too low (Attempt {attempt}). Retrying...",
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "quality_overall": quality_result['overall'],
                        "quality_issues": quality_result['issues'],
                        "status": "quality_retry"
                    })
                    
                    # Clean up low-quality image
                    os.remove(current_image_path)
                    
                    if attempt < max_attempts:
                        logger.info(f"Waiting {wait_seconds} seconds before next attempt...")
                        await asyncio.sleep(wait_seconds)
                    else:
                        with self.lock:
                            self.status['retry_stats']['max_retries_reached'] += 1
                            self._save_status()
                        await self.send_websocket_notification("automation_status", {
                            "message": "Max retries reached for image capture due to low quality.",
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "status": "max_retries_reached"
                        })
                        raise Exception("Max retries reached for image capture due to low quality.")
                else:
                    image_path = current_image_path
                    logger.info(f"Successfully captured a quality image on attempt {attempt}.")
                    await self.send_websocket_notification("automation_status", {
                        "message": f"Quality image captured on attempt {attempt}",
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "quality_overall": quality_result['overall'],
                        "status": "quality_passed"
                    })
            # END RETRY LOOP
            
            if not image_path:
                raise Exception("Failed to capture image from camera after all attempts")

            # Process attendance
            result = await self.face_service.process_attendance_image(
                image_path, 
                self.settings['class_name']
            )

            # Save attendance record
            attendance_id = await self.attendance_service.save_attendance(
                class_name=self.settings['class_name'],
                image_path=image_path,
                present_students=result['present'],
                absent_students=result['absent'],
                total_faces_detected=result['total_faces_detected']
            )

            # Update status
            with self.lock:
                self.status['last_run'] = datetime.now().isoformat()
                self.status['total_runs'] += 1
                self.status['successful_runs'] += 1
                self._save_status()

            logger.info(f"Automated attendance completed successfully. ID: {attendance_id}")
            logger.info(f"Present: {len(result['present'])}, Absent: {len(result['absent'])}")
            
            # Send success notification via WebSocket
            await self.send_websocket_notification("attendance_completed", {
                "message": "Automated attendance completed successfully",
                "attendance_id": attendance_id,
                "present_count": len(result['present']),
                "absent_count": len(result['absent']),
                "total_faces_detected": result['total_faces_detected'],
                "class_name": self.settings['class_name'],
                "status": "success"
            })

        except Exception as e:
            logger.error(f"Error in automated attendance cycle: {e}")
            with self.lock:
                self.status['failed_runs'] += 1
                self._save_status()

    async def automation_loop(self):
        """Main automation loop"""
        logger.info("Automation loop started")
        
        while self.is_running:
            try:
                # Run attendance cycle
                await self.run_attendance_cycle()

                # Calculate next run time
                interval_seconds = self.settings['interval_minutes'] * 60
                next_run = datetime.now() + timedelta(seconds=interval_seconds)
                
                with self.lock:
                    self.status['next_run'] = next_run.isoformat()
                    self._save_status()

                # Wait for next cycle
                logger.info(f"Next automated attendance at: {next_run}")
                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                logger.info("Automation loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)

        logger.info("Automation loop stopped")

    async def start(self, class_name: str, schedule: Optional[Dict] = None) -> Dict[str, Any]:
        """Start automated attendance"""
        if self.is_running:
            return {"message": "Automation is already running", "status": self.status}

        # Update settings
        self.settings['class_name'] = class_name
        self.settings['enabled'] = True
        self._save_settings()

        # Reset and update status
        with self.lock:
            self.is_running = True
            self.status['is_running'] = True
            self.status['next_run'] = datetime.now().isoformat()
            self._save_status()

        # Start automation loop in background
        self.task = asyncio.create_task(self.automation_loop())

        logger.info(f"Automated attendance started for class: {class_name}")
        return {"message": "Automation started successfully", "status": self.status}

    async def stop(self) -> Dict[str, Any]:
        """Stop automated attendance"""
        if not self.is_running:
            return {"message": "Automation is not running", "status": self.status}

        # Stop the loop
        self.is_running = False
        self.settings['enabled'] = False
        self._save_settings()

        # Cancel the task
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        # Update status
        with self.lock:
            self.status['is_running'] = False
            self.status['next_run'] = None
            self._save_status()

        logger.info("Automated attendance stopped")
        return {"message": "Automation stopped successfully", "status": self.status}

    async def get_logs(self, limit: int = 50) -> list:
        """Get automation logs (placeholder for future implementation)"""
        # This could be implemented to read from a log file
        return []
