from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.models.database import DatabaseManager
from app.core.security import (
    get_password_hash,
    verify_password,
    create_token_response,
    generate_invite_code,
    INVITE_CODE_EXPIRE_DAYS
)
from app.models.auth_schemas import UserCreate, TeacherRegister, StudentRegister, UserLogin

class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    async def register_teacher(teacher_data: TeacherRegister) -> Dict:
        """Register a new teacher"""
        # Check if email already exists
        existing_user = DatabaseManager.execute_query(
            "SELECT id FROM users WHERE email = ?",
            (teacher_data.email,)
        )
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = get_password_hash(teacher_data.password)
        
        # Create user
        user_id = DatabaseManager.execute_insert(
            """INSERT INTO users (email, password_hash, full_name, role, is_active)
               VALUES (?, ?, ?, 'teacher', 1)""",
            (teacher_data.email, password_hash, teacher_data.full_name)
        )
        
        # Get created user
        user = DatabaseManager.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            raise ValueError("Failed to create user")
        
        return user[0]
    
    @staticmethod
    async def register_student(student_data: StudentRegister) -> Dict:
        """Register a new student with optional invite code"""
        class_name = "Unassigned"  # Default class for students without invite code
        class_id = None
        
        # Check if invite code is provided
        if student_data.invite_code and student_data.invite_code.strip():
            # Trim whitespace from invite code
            invite_code = student_data.invite_code.strip().upper()
            
            print(f"DEBUG: Registering student with invite code: '{invite_code}'")
            
            # Validate invite code
            class_info = DatabaseManager.execute_query(
                """SELECT id, class_name, invite_expires_at 
                   FROM classes 
                   WHERE UPPER(invite_code) = ?""",
                (invite_code,)
            )
            
            print(f"DEBUG: Class info result: {class_info}")
            
            if not class_info:
                raise ValueError("Invalid invite code")
            
            class_data = class_info[0]
            
            # Check if invite code has expired
            if class_data.get('invite_expires_at'):
                expires_at = datetime.fromisoformat(class_data['invite_expires_at'])
                if expires_at < datetime.now():
                    raise ValueError("Invite code has expired")
            
            class_name = class_data['class_name']
            class_id = class_data['id']
        else:
            print("DEBUG: Registering student without invite code (independent registration)")
        
        # Check if email already exists
        existing_user = DatabaseManager.execute_query(
            "SELECT id FROM users WHERE email = ?",
            (student_data.email,)
        )
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if student_id already exists
        existing_student = DatabaseManager.execute_query(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_data.student_id,)
        )
        
        if existing_student:
            raise ValueError("Student ID already registered")
        
        # Hash password
        password_hash = get_password_hash(student_data.password)
        
        # Create user
        user_id = DatabaseManager.execute_insert(
            """INSERT INTO users (email, password_hash, full_name, role, is_active)
               VALUES (?, ?, ?, 'student', 1)""",
            (student_data.email, password_hash, student_data.full_name)
        )
        
        # Create student record (class_name can be NULL if no invite code)
        DatabaseManager.execute_insert(
            """INSERT INTO students (student_id, name, class_name, user_id)
               VALUES (?, ?, ?, ?)""",
            (student_data.student_id, student_data.full_name, class_name, user_id)
        )
        
        # Enroll student in class if invite code was provided
        if class_id:
            DatabaseManager.execute_insert(
                """INSERT INTO class_enrollments (class_id, student_id)
                   VALUES (?, ?)""",
                (class_id, user_id)
            )
            print(f"DEBUG: Student enrolled in class {class_name}")
        else:
            print("DEBUG: Student registered without class enrollment")
        
        # Get created user
        user = DatabaseManager.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            raise ValueError("Failed to create user")
        
        return user[0]
    
    @staticmethod
    async def login(login_data: UserLogin) -> Dict:
        """Authenticate user and return token"""
        # Get user by email
        user = DatabaseManager.execute_query(
            "SELECT * FROM users WHERE email = ?",
            (login_data.email,)
        )
        
        if not user:
            raise ValueError("Invalid email or password")
        
        user_data = user[0]
        
        # Verify password
        if not verify_password(login_data.password, user_data['password_hash']):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user_data['is_active']:
            raise ValueError("Account is deactivated")
        
        # Create access token
        access_token = create_token_response(
            user_id=user_data['id'],
            email=user_data['email'],
            role=user_data['role']
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_data['id'],
                "email": user_data['email'],
                "full_name": user_data['full_name'],
                "role": user_data['role'],
                "is_active": user_data['is_active'],
                "created_at": user_data['created_at']
            }
        }
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        user = DatabaseManager.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            return None
        
        return user[0]
    
    @staticmethod
    async def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        # Get user
        user = DatabaseManager.execute_query(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user[0]['password_hash']):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = get_password_hash(new_password)
        
        # Update password
        DatabaseManager.execute_update(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_password_hash, user_id)
        )
        
        return True
