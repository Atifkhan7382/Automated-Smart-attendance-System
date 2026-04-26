import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import shutil
from typing import List, Optional
import json
from datetime import datetime, date
import pandas as pd

from app.services.face_recognition import FaceRecognitionService
from app.services.attendance import AttendanceService
from app.services.student_management import StudentManagementService
from app.services.automation import AutomationService
from app.models.database import init_db
from app.models.schemas import StudentCreate, AttendanceRecord, AttendanceReport

# Import optimized endpoints
from app.api.endpoints.optimized_attendance import router as optimized_attendance_router
# from app.api.endpoints.students import router as students_router  # Disabled - using student_router instead
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.teacher import router as teacher_router
from app.api.endpoints.student import router as student_router
from app.api.endpoints.settings import router as settings_router
from app.api.endpoints.verification import router as verification_router

app = FastAPI(
    title="AttendAI",
    description="AI-powered face recognition attendance management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("data/student_images", exist_ok=True)
os.makedirs("data/attendance_images", exist_ok=True)
os.makedirs("data/encodings", exist_ok=True)

app.mount("/static", StaticFiles(directory="data"), name="static")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(teacher_router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(student_router, prefix="/api/student", tags=["Student"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])
app.include_router(optimized_attendance_router, prefix="/api/optimized", tags=["Optimized Attendance"])
app.include_router(verification_router, prefix="/api/verification", tags=["Teacher Verification"])
# app.include_router(students_router, prefix="/api/students", tags=["Students"])  # Disabled - conflicts with student_router

# Initialize services
face_service = FaceRecognitionService()
attendance_service = AttendanceService()
student_service = StudentManagementService()
automation_service = None  # Will be initialized after face_service is ready

@app.on_event("startup")
async def startup_event():
    global automation_service
    init_db()
    # Load existing face encodings
    await face_service.load_encodings()
    # Initialize automation service
    automation_service = AutomationService(face_service, attendance_service)

@app.get("/")
async def root():
    return {"message": "AttendAI API", "version": "1.0.0"}

# Old student management endpoints removed - now using /api/students/* router

# Old student endpoints removed - now using /api/students/* router

# Attendance Endpoints
@app.post("/api/attendance/mark")
async def mark_attendance(
    class_name: str = Form(...),
    file: UploadFile = File(...)
):
    """Process classroom image and mark attendance with strict quality validation"""
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save attendance image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_{class_name}_{timestamp}_{file.filename}"
        file_path = f"data/attendance_images/{filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # QUALITY VALIDATION FOR MANUAL ATTENDANCE
        quality_validation_enabled = True  # Can be configured in settings
        min_quality_threshold = 0.7  # Strict threshold for manual uploads
        
        if quality_validation_enabled and hasattr(face_service, 'quality_assessor') and face_service.quality_assessor is not None:
            try:
                import cv2
                import numpy as np
                
                # Load image
                image = cv2.imread(file_path)
                if image is None:
                    raise HTTPException(status_code=400, detail="Failed to load uploaded image")
                
                # Detect faces
                faces = face_service.face_analyzer.get(image)
                if len(faces) == 0:
                    # Clean up file
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "error": "No faces detected",
                            "message": "No faces were detected in the uploaded image",
                            "suggestions": [
                                "Ensure students are clearly visible in the image",
                                "Check that the image is not too dark or blurry",
                                "Make sure the camera is positioned to capture faces directly"
                            ]
                        }
                    )
                
                # Assess quality of detected faces
                quality_issues = []
                low_quality_faces = 0
                
                for i, face in enumerate(faces):
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    face_image = image[y1:y2, x1:x2]
                    
                    # Assess quality
                    quality_result = face_service.quality_assessor.assess_quality(face_image)
                    
                    if quality_result['overall'] < min_quality_threshold:
                        low_quality_faces += 1
                        # Identify specific issues
                        if quality_result['blur'] < 0.5:
                            quality_issues.append(f"Face #{i+1}: Image is blurry")
                        if quality_result['brightness'] < 0.5:
                            quality_issues.append(f"Face #{i+1}: Poor lighting (too dark or too bright)")
                        if quality_result['size'] < 0.5:
                            quality_issues.append(f"Face #{i+1}: Face too small in frame")
                        if quality_result['contrast'] < 0.5:
                            quality_issues.append(f"Face #{i+1}: Low contrast")
                
                # If too many low-quality faces, reject the image
                if low_quality_faces > len(faces) * 0.3:  # More than 30% low quality
                    # Clean up file
                    os.remove(file_path)
                    
                    # Build detailed error response
                    error_detail = {
                        "error": "Image quality too low",
                        "message": f"{low_quality_faces} out of {len(faces)} detected faces have quality issues",
                        "quality_threshold": min_quality_threshold,
                        "issues": quality_issues[:10],  # Limit to first 10 issues
                        "suggestions": [
                            "Ensure good lighting conditions",
                            "Use a stable camera or tripod to avoid blur",
                            "Position camera closer to students for larger face sizes",
                            "Avoid backlighting (light source behind students)",
                            "Clean camera lens if image appears blurry"
                        ]
                    }
                    
                    raise HTTPException(status_code=422, detail=error_detail)
                
            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except Exception as e:
                # Log quality check error but continue with attendance processing
                print(f"Quality check error (non-fatal): {e}")
        
        # Process attendance
        result = await face_service.process_attendance_image(file_path, class_name)
        
        # Save attendance record
        attendance_id = await attendance_service.save_attendance(
            class_name=class_name,
            image_path=file_path,
            present_students=result['present'],
            absent_students=result['absent'],
            total_faces_detected=result['total_faces_detected']
        )
        
        # Save verification records if any
        pending_verifications_data = []
        if result.get('pending_verifications'):
            from app.utils.verification_manager import VerificationManager
            verification_manager = VerificationManager()
            
            for verification in result['pending_verifications']:
                try:
                    verification_manager.create_verification_record(
                        attendance_record_id=attendance_id,
                        face_index=verification['face_index'],
                        face_crop=verification['face_crop'],
                        bbox=verification['bbox'],
                        quality_score=verification['quality_score'],
                        suggested_student_id=verification['suggested_student_id'],
                        suggested_similarity=verification['suggested_similarity']
                    )
                except Exception as e:
                    print(f"Failed to save verification record: {e}")
            
            # Fetch verification records with base64 encoding
            pending_verifications_data = verification_manager.get_pending_verifications(attendance_id)
        
        return {
            "attendance_id": attendance_id,
            "class_name": class_name,
            "timestamp": datetime.now().isoformat(),
            "present": result['present'],
            "absent": result['absent'],
            "total_students": len(result['present']) + len(result['absent']),
            "total_faces_detected": result['total_faces_detected'],
            "attendance_percentage": (len(result['present']) / (len(result['present']) + len(result['absent'])) * 100) if (len(result['present']) + len(result['absent'])) > 0 else 0,
            "pending_verifications": pending_verifications_data,
            "has_pending_verifications": len(pending_verifications_data) > 0
        }
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions with their original status codes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/report")
async def get_attendance_report(
    class_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Generate attendance report"""
    try:
        return await attendance_service.generate_report(class_name, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/export")
async def export_attendance(
    class_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export attendance data as Excel file"""
    try:
        file_path = await attendance_service.export_to_excel(class_name, start_date, end_date)
        return {"download_url": f"/static/exports/{os.path.basename(file_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/session/{session_id}/export")
async def export_session_attendance(session_id: int):
    """Export individual session attendance report as Excel file"""
    try:
        file_path = await attendance_service.export_session_to_excel(session_id)
        return {"download_url": f"/static/exports/{os.path.basename(file_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/attendance/session/{session_id}")
async def delete_session_attendance(session_id: int):
    """Delete a specific attendance session"""
    try:
        success = await attendance_service.delete_attendance_record(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/attendance/clear-all")
async def clear_all_attendance():
    """Clear all attendance history"""
    try:
        success = await attendance_service.clear_all_history()
        if success:
            return {"message": "All attendance history cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_statistics():
    """Get system statistics"""
    try:
        stats = await attendance_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gpu-status")
async def get_gpu_status():
    """Get GPU acceleration status"""
    try:
        gpu_status = face_service.gpu_manager.get_status()
        return {
            "gpu_acceleration": gpu_status,
            "performance_info": {
                "image_processing": "GPU" if gpu_status['gpu_available'] else "CPU",
                "face_detection": "Optimized" if gpu_status['gpu_available'] else "Standard",
                "recommended_settings": {
                    "num_jitters": face_service.num_jitters,
                    "face_detection_upsamples": face_service.face_detection_upsamples,
                    "face_detection_model": face_service.face_detection_model
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/attendance/clear-all")
async def clear_all_attendance_history():
    """Clear all attendance history (keeps students)"""
    try:
        success = await attendance_service.clear_all_history()
        if success:
            return {"message": "All attendance history cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear attendance history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/attendance/{record_id}")
async def delete_attendance_record(record_id: int):
    """Delete a specific attendance record"""
    try:
        success = await attendance_service.delete_attendance_record(record_id)
        if success:
            return {"message": "Attendance record deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Attendance record not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/session/{attendance_id}")
async def get_session_report(attendance_id: int):
    """Get detailed session attendance report with student names and presence status"""
    try:
        report = await attendance_service.generate_session_report(attendance_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/session/{attendance_id}/export")
async def export_session_attendance(attendance_id: int):
    """Export session attendance report to Excel file"""
    try:
        file_path = await attendance_service.export_session_to_excel(attendance_id)
        return {"download_url": f"/static/exports/{os.path.basename(file_path)}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/system/reset")
async def reset_entire_system():
    """Reset entire system - delete all students and attendance data"""
    try:
        # Clear all attendance data
        await attendance_service.clear_all_history()
        
        # Clear all students
        success = await student_service.clear_all_students()
        
        # Clear face encodings
        await face_service.clear_all_encodings()
        
        if success:
            return {"message": "Entire system reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset system")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model Status Endpoint
@app.get("/api/model/status")
async def get_model_status():
    """Get face recognition model status"""
    try:
        # Check if encodings are loaded
        encodings_file = "data/encodings/face_encodings.pkl"
        if os.path.exists(encodings_file):
            import pickle
            with open(encodings_file, 'rb') as f:
                encodings = pickle.load(f)
            
            return {
                "status": "trained",
                "version": "1.0.0",
                "accuracy": 95.0,
                "num_classes": len(encodings),
                "created_at": datetime.fromtimestamp(os.path.getmtime(encodings_file)).isoformat()
            }
        else:
            return {
                "status": "not_trained",
                "version": None,
                "accuracy": None,
                "num_classes": 0,
                "created_at": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Automation Endpoints
@app.get("/api/automation/settings")
async def get_automation_settings():
    """Get automation settings"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        return await automation_service.get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/settings")
async def update_automation_settings(settings: dict):
    """Update automation settings"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        return await automation_service.update_settings(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/status")
async def get_automation_status():
    """Get automation status"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        return await automation_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/start")
async def start_automation(data: dict):
    """Start automated attendance"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        
        class_name = data.get('class_name')
        schedule = data.get('schedule')
        
        if not class_name:
            raise HTTPException(status_code=400, detail="class_name is required")
        
        result = await automation_service.start(class_name, schedule)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/stop")
async def stop_automation():
    """Stop automated attendance"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        result = await automation_service.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/status")
async def get_automation_status():
    """Get automation status"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        status = await automation_service.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/settings")
async def get_automation_settings():
    """Get automation settings"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        settings = await automation_service.get_settings()
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/settings")
async def update_automation_settings(settings: dict):
    """Update automation settings"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        updated_settings = await automation_service.update_settings(settings)
        return updated_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/logs")
async def get_automation_logs(limit: int = 50):
    """Get automation logs"""
    try:
        if automation_service is None:
            raise HTTPException(status_code=503, detail="Automation service not initialized")
        logs = await automation_service.get_logs(limit)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/face-recognition/rebuild")
async def rebuild_face_encodings():
    """Rebuild all face encodings from student images"""
    try:
        print("🔧 Rebuilding face encodings...")
        
        # Clear existing encodings
        await face_service.clear_all_encodings()
        print("✅ Cleared existing encodings")
        
        # Get all students
        students = await student_service.get_students()
        print(f"✅ Found {len(students)} students")
        
        total_encodings = 0
        successful_students = 0
        failed_students = []
        
        # Process each student
        for student in students:
            student_id = student['student_id']
            student_name = student['name']
            print(f"🎯 Processing: {student_name} ({student_id})")
            
            # Check student directory
            student_dir = f"data/student_images/{student_id}"
            if os.path.exists(student_dir):
                images = [f for f in os.listdir(student_dir) if f.endswith('.jpg')]
                print(f"   📸 Found {len(images)} images")
                
                student_encodings = 0
                # Process each image
                for i, image_file in enumerate(images):
                    image_path = os.path.join(student_dir, image_file)
                    print(f"   🔍 Processing {i+1}/{len(images)}: {image_file}")
                    
                    try:
                        encoding = await face_service.generate_encoding(image_path, student_id)
                        if encoding is not None:
                            student_encodings += 1
                            total_encodings += 1
                            print(f"      ✅ Generated encoding")
                        else:
                            print(f"      ❌ No face detected in {image_file}")
                    except Exception as e:
                        print(f"      ❌ Error processing {image_file}: {e}")
                
                if student_encodings > 0:
                    successful_students += 1
                    print(f"   🎉 Student {student_name} processed with {student_encodings} encodings")
                else:
                    failed_students.append(student_name)
                    print(f"   ❌ Failed to generate encodings for {student_name}")
            else:
                failed_students.append(student_name)
                print(f"   ⚠️  No directory found for {student_id}")
        
        # Save encodings
        print("💾 Saving encodings...")
        await face_service.save_encodings()
        print("✅ Encodings saved successfully")
        
        # Verify results
        await face_service.load_encodings()
        print(f"📊 Final: {len(face_service.known_face_encodings)} students with encodings")
        
        return {
            "success": True,
            "message": "Face encodings rebuilt successfully",
            "total_students": len(students),
            "successful_students": successful_students,
            "failed_students": failed_students,
            "total_encodings": total_encodings,
            "students_with_encodings": len(face_service.known_face_encodings)
        }
        
    except Exception as e:
        print(f"❌ Error rebuilding encodings: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)