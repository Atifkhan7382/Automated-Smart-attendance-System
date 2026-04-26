from fastapi import APIRouter, HTTPException, Depends, status
from app.models.auth_schemas import (
    TeacherRegister, StudentRegister, UserLogin, 
    TokenResponse, UserResponse, PasswordChange
)
from app.services.auth_service import AuthService
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register/teacher", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_teacher(teacher_data: TeacherRegister):
    """Register a new teacher"""
    try:
        user = await AuthService.register_teacher(teacher_data)
        return UserResponse(
            id=user['id'],
            email=user['email'],
            full_name=user['full_name'],
            role=user['role'],
            is_active=user['is_active'],
            created_at=user['created_at']
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/register/student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_student(student_data: StudentRegister):
    """Register a new student using an invite code"""
    try:
        user = await AuthService.register_student(student_data)
        return UserResponse(
            id=user['id'],
            email=user['email'],
            full_name=user['full_name'],
            role=user['role'],
            is_active=user['is_active'],
            created_at=user['created_at']
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """Login and get access token"""
    try:
        result = await AuthService.login(login_data)
        return TokenResponse(
            access_token=result['access_token'],
            token_type=result['token_type'],
            user=UserResponse(**result['user'])
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        user = await AuthService.get_user_by_id(current_user['id'])
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            full_name=user['full_name'],
            role=user['role'],
            is_active=user['is_active'],
            created_at=user['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        success = await AuthService.change_password(
            user_id=current_user['id'],
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to change password")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout (client should discard token)"""
    # In a stateless JWT system, logout is handled client-side by discarding the token
    # For additional security, you could implement a token blacklist here
    return {"message": "Logged out successfully"}
