from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import List, Optional
from app.models.auth_schemas import (
    ClassCreate, ClassUpdate, ClassResponse, 
    InviteLinkResponse, StudentEnrollment
)
from app.services.class_service import ClassService
from app.api.deps import get_current_teacher

router = APIRouter()

@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: dict = Depends(get_current_teacher)
):
    """Create a new class"""
    try:
        class_info = await ClassService.create_class(
            teacher_id=current_user['id'],
            class_name=class_data.class_name,
            description=class_data.description
        )
        
        return ClassResponse(
            id=class_info['id'],
            class_name=class_info['class_name'],
            teacher_id=class_info['teacher_id'],
            description=class_info.get('description'),
            invite_code=class_info.get('invite_code'),
            invite_expires_at=class_info.get('invite_expires_at'),
            created_at=class_info['created_at'],
            student_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/classes", response_model=List[ClassResponse])
async def get_teacher_classes(current_user: dict = Depends(get_current_teacher)):
    """Get all classes for the current teacher"""
    try:
        classes = await ClassService.get_teacher_classes(current_user['id'])
        
        return [
            ClassResponse(
                id=c['id'],
                class_name=c['class_name'],
                teacher_id=c['teacher_id'],
                description=c.get('description'),
                invite_code=c.get('invite_code'),
                invite_expires_at=c.get('invite_expires_at'),
                created_at=c['created_at'],
                student_count=c.get('student_count', 0)
            )
            for c in classes
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/classes/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    current_user: dict = Depends(get_current_teacher)
):
    """Get a specific class"""
    try:
        class_info = await ClassService.get_class_by_id(class_id, current_user['id'])
        
        if not class_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        
        # Get student count
        students = await ClassService.get_class_students(class_id, current_user['id'])
        
        return ClassResponse(
            id=class_info['id'],
            class_name=class_info['class_name'],
            teacher_id=class_info['teacher_id'],
            description=class_info.get('description'),
            invite_code=class_info.get('invite_code'),
            invite_expires_at=class_info.get('invite_expires_at'),
            created_at=class_info['created_at'],
            student_count=len(students)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/classes/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: dict = Depends(get_current_teacher)
):
    """Update a class"""
    try:
        class_info = await ClassService.update_class(
            class_id=class_id,
            teacher_id=current_user['id'],
            class_name=class_data.class_name,
            description=class_data.description
        )
        
        if not class_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        
        return ClassResponse(
            id=class_info['id'],
            class_name=class_info['class_name'],
            teacher_id=class_info['teacher_id'],
            description=class_info.get('description'),
            invite_code=class_info.get('invite_code'),
            invite_expires_at=class_info.get('invite_expires_at'),
            created_at=class_info['created_at'],
            student_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: int,
    current_user: dict = Depends(get_current_teacher)
):
    """Delete a class"""
    try:
        success = await ClassService.delete_class(class_id, current_user['id'])
        
        if success:
            return {"message": "Class deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/classes/{class_id}/invite", response_model=InviteLinkResponse)
async def generate_invite_link(
    class_id: int,
    request: Request,
    current_user: dict = Depends(get_current_teacher)
):
    """Generate an invite link for a class"""
    try:
        # Get base URL from request
        base_url = str(request.base_url).rstrip('/')
        # Use frontend URL instead of backend URL
        frontend_url = base_url.replace(':8000', ':3000')
        
        invite_info = await ClassService.generate_invite_link(
            class_id=class_id,
            teacher_id=current_user['id'],
            base_url=frontend_url
        )
        
        return InviteLinkResponse(**invite_info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/classes/{class_id}/students", response_model=List[StudentEnrollment])
async def get_class_students(
    class_id: int,
    current_user: dict = Depends(get_current_teacher)
):
    """Get all students in a class"""
    try:
        students = await ClassService.get_class_students(class_id, current_user['id'])
        
        return [
            StudentEnrollment(
                student_id=s['student_id'],
                student_name=s['student_name'],
                student_email=s['student_email'],
                enrolled_at=s['enrolled_at'],
                attendance_percentage=s.get('attendance_percentage', 0.0)
            )
            for s in students
        ]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/classes/{class_id}/students/{student_id}")
async def remove_student_from_class(
    class_id: int,
    student_id: int,
    current_user: dict = Depends(get_current_teacher)
):
    """Remove a student from a class"""
    try:
        success = await ClassService.remove_student_from_class(
            class_id=class_id,
            student_id=student_id,
            teacher_id=current_user['id']
        )
        
        if success:
            return {"message": "Student removed from class successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found in class")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
