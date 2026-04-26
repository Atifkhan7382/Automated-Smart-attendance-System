from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import decode_access_token
from app.models.database import DatabaseManager

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get the current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    email: str = payload.get("email")
    role: str = payload.get("role")
    
    if user_id is None or email is None:
        raise credentials_exception
    
    # Verify user exists and is active
    user = DatabaseManager.execute_query(
        "SELECT * FROM users WHERE id = ? AND is_active = 1",
        (int(user_id),)
    )
    
    if not user:
        raise credentials_exception
    
    return {
        "id": int(user_id),
        "email": email,
        "role": role,
        "full_name": user[0].get("full_name") if user else ""
    }

async def get_current_teacher(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure the current user is a teacher
    """
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this resource"
        )
    return current_user

async def get_current_student(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure the current user is a student
    """
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this resource"
        )
    return current_user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Dependency to get the current user if authenticated, otherwise None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
