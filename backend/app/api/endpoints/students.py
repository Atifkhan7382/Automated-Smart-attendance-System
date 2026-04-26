"""
Student Management API Endpoints
Handles student CRUD operations with Firebase Storage integration
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import os
import shutil
from datetime import datetime

from app.services.student_management import StudentManagementService
from app.services.face_recognition import FaceRecognitionService
from app.utils.firebase_storage import FirebaseStorageManager
from app.services.yolov8_attendance import YOLOv8AttendanceService

router = APIRouter()

# Initialize services
student_service = StudentManagementService()
face_service = FaceRecognitionService()
firebase_storage = FirebaseStorageManager()


@router.post("/")
async def create_student(
    name: str = Form(...),
    student_id: str = Form(...),
    class_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Add a new student with image upload (root endpoint for frontend compatibility)
    """
    local_path = None
    student_dir = None
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check if student already exists
        existing = await student_service.get_student_by_id(student_id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Student ID {student_id} already exists")
        
        # Save student image locally first
        student_dir = f"data/student_images/{student_id}"
        os.makedirs(student_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{student_id}_{timestamp}_{file.filename}"
        local_path = f"{student_dir}/{filename}"
        
        with open(local_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"💾 Saved locally: {local_path}")
        
        # Upload to Firebase Storage
        firebase_url = await firebase_storage.upload_student_image(local_path, student_id)
        
        # Store Firebase URL in database (or local path if Firebase unavailable)
        image_path = firebase_url if firebase_url else local_path
        
        # Create student record in database
        student = await student_service.create_student(name, student_id, class_name, image_path)
        
        # Generate YOLOv8 face encoding
        try:
            yolo_service = YOLOv8AttendanceService(student_service)
            success = await yolo_service.enroll_student_faces(student_id, local_path)
            
            if not success:
                print(f"⚠️ Warning: Could not generate face encoding for student {student_id}")
        except Exception as e:
            print(f"⚠️ Face encoding error: {e}")
        
        return {
            "success": True,
            "message": "Student added successfully",
            "student": student,
            "image_url": image_path,
            "firebase_uploaded": bool(firebase_url)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if student_dir and os.path.exists(student_dir):
            shutil.rmtree(student_dir, ignore_errors=True)
        
        print(f"❌ Error adding student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_student(
    name: str = Form(...),
    student_id: str = Form(...),
    class_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Add a new student with image upload to Firebase Storage
    """
    local_path = None
    student_dir = None
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check if student already exists
        existing = await student_service.get_student_by_id(student_id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Student ID {student_id} already exists")
        
        # Save student image locally first
        student_dir = f"data/student_images/{student_id}"
        os.makedirs(student_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{student_id}_{timestamp}_{file.filename}"
        local_path = f"{student_dir}/{filename}"
        
        with open(local_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"💾 Saved locally: {local_path}")
        
        # Upload to Firebase Storage
        firebase_url = await firebase_storage.upload_student_image(local_path, student_id)
        
        # Store Firebase URL in database (or local path if Firebase unavailable)
        image_path = firebase_url if firebase_url else local_path
        
        # Create student record in database
        student = await student_service.create_student(name, student_id, class_name, image_path)
        
        # Generate YOLOv8 face encoding
        try:
            yolo_service = YOLOv8AttendanceService(student_service)
            success = await yolo_service.enroll_student_faces(student_id, local_path)
            
            if not success:
                print(f"⚠️ Warning: Could not generate face encoding for student {student_id}")
        except Exception as e:
            print(f"⚠️ Face encoding error: {e}")
        
        return {
            "success": True,
            "message": "Student added successfully",
            "student": student,
            "image_url": image_path,
            "firebase_uploaded": bool(firebase_url)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if student_dir and os.path.exists(student_dir):
            shutil.rmtree(student_dir, ignore_errors=True)
        
        print(f"❌ Error adding student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video")
async def create_student_from_video(
    name: str = Form(...),
    student_id: str = Form(...),
    class_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Add a new student by extracting faces from video
    """
    video_path = None
    student_dir = None
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Check if student already exists
        existing = await student_service.get_student_by_id(student_id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Student ID {student_id} already exists")
        
        # Save video temporarily
        student_dir = f"data/student_images/{student_id}"
        os.makedirs(student_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"{student_id}_{timestamp}_{file.filename}"
        video_path = f"{student_dir}/{video_filename}"
        
        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"💾 Saved video: {video_path}")
        
        # Extract faces from video
        import cv2
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_interval = max(fps // 2, 1)  # Extract 2 frames per second
        
        frame_count = 0
        saved_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_filename = f"{student_id}_frame_{saved_count}.jpg"
                frame_path = f"{student_dir}/{frame_filename}"
                cv2.imwrite(frame_path, frame)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        
        # Remove video file after extraction
        if os.path.exists(video_path):
            os.remove(video_path)
        
        if saved_count == 0:
            raise HTTPException(status_code=400, detail="No frames could be extracted from video")
        
        print(f"✅ Extracted {saved_count} frames from video")
        
        # Use first frame as primary image
        first_frame = f"{student_dir}/{student_id}_frame_0.jpg"
        
        # Upload first frame to Firebase
        firebase_url = await firebase_storage.upload_student_image(first_frame, student_id)
        image_path = firebase_url if firebase_url else first_frame
        
        # Create student record
        student = await student_service.create_student(name, student_id, class_name, image_path)
        
        # Generate YOLOv8 face encodings from all frames
        try:
            yolo_service = YOLOv8AttendanceService(student_service)
            success = await yolo_service.enroll_student_faces(student_id, first_frame)
            
            if not success:
                print(f"⚠️ Warning: Could not generate face encoding for student {student_id}")
        except Exception as e:
            print(f"⚠️ Face encoding error: {e}")
        
        return {
            "success": True,
            "message": "Student added successfully from video",
            "student": student,
            "frames_extracted": saved_count,
            "faces_detected": saved_count,
            "image_url": image_path,
            "firebase_uploaded": bool(firebase_url)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if student_dir and os.path.exists(student_dir):
            shutil.rmtree(student_dir, ignore_errors=True)
        
        print(f"❌ Error adding student from video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_students(class_name: Optional[str] = None):
    """
    Get all students, optionally filtered by class (root endpoint)
    """
    try:
        students = await student_service.get_students(class_name)
        return {
            "success": True,
            "count": len(students),
            "students": students
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_students(class_name: Optional[str] = None):
    """
    Get all students, optionally filtered by class (legacy endpoint)
    """
    try:
        students = await student_service.get_students(class_name)
        return {
            "success": True,
            "count": len(students),
            "students": students
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}")
async def get_student(student_id: str):
    """
    Get a specific student by ID
    """
    try:
        student = await student_service.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "success": True,
            "student": student
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{student_id}")
async def update_student(
    student_id: str,
    name: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Update student information and/or image
    """
    try:
        # Check if student exists
        existing = await student_service.get_student_by_id(student_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Student not found")
        
        image_path = None
        
        # Handle new image upload
        if file:
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Save new image
            student_dir = f"data/student_images/{student_id}"
            os.makedirs(student_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{student_id}_{timestamp}_{file.filename}"
            local_path = f"{student_dir}/{filename}"
            
            with open(local_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Upload to Firebase
            firebase_url = await firebase_storage.upload_student_image(local_path, student_id)
            image_path = firebase_url if firebase_url else local_path
            
            # Regenerate face encoding with new image
            try:
                yolo_service = YOLOv8AttendanceService(student_service)
                await yolo_service.enroll_student_faces(student_id, local_path)
            except Exception as e:
                print(f"⚠️ Face encoding update error: {e}")
        
        # Update student record
        updated_student = await student_service.update_student(
            student_id,
            name=name,
            class_name=class_name,
            image_path=image_path
        )
        
        return {
            "success": True,
            "message": "Student updated successfully",
            "student": updated_student
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}")
async def delete_student(student_id: str):
    """
    Delete a student and all associated data from database and Firebase Storage
    """
    try:
        # Get student info before deletion
        student = await student_service.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Delete from Firebase Storage
        firebase_path = f"students/{student_id}"
        
        if firebase_storage.bucket:
            try:
                # List all blobs with this prefix
                blobs = firebase_storage.bucket.list_blobs(prefix=firebase_path)
                
                deleted_count = 0
                for blob in blobs:
                    try:
                        blob.delete()
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {blob.name}: {e}")
                
                if deleted_count > 0:
                    print(f"✅ Deleted {deleted_count} images from Firebase for student {student_id}")
            except Exception as e:
                print(f"⚠️ Firebase deletion error: {e}")
        
        # Delete from local storage
        student_dir = f"data/student_images/{student_id}"
        if os.path.exists(student_dir):
            shutil.rmtree(student_dir, ignore_errors=True)
            print(f"✅ Deleted local images for student {student_id}")
        
        # Delete from database
        await student_service.delete_student(student_id)
        
        # Remove face encoding
        try:
            yolo_service = YOLOv8AttendanceService(student_service)
            if student_id in yolo_service.face_descriptors:
                del yolo_service.face_descriptors[student_id]
                yolo_service._save_encodings()
                print(f"✅ Removed face encoding for student {student_id}")
        except Exception as e:
            print(f"⚠️ Face encoding removal error: {e}")
        
        return {
            "success": True,
            "message": f"Student {student_id} deleted successfully from database and Firebase Storage"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes/list")
async def list_classes():
    """
    Get list of all unique classes
    """
    try:
        classes = await student_service.get_classes()
        return {
            "success": True,
            "count": len(classes),
            "classes": classes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes/{class_name}/stats")
async def get_class_stats(class_name: str):
    """
    Get statistics for a specific class
    """
    try:
        stats = await student_service.get_class_statistics(class_name)
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
