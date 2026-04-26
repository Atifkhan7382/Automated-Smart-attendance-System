"""
Firebase Firestore Database Implementation
Free forever! No credit card required.
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
from typing import Dict, List, Optional
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase
_firebase_initialized = False
db = None
bucket = None

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized, db, bucket
    
    if _firebase_initialized:
        return db, bucket
    
    try:
        # Check for Firebase credentials
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        
        if os.path.exists(cred_path):
            # Production: Load from file
            cred = credentials.Certificate(cred_path)
        elif os.getenv('FIREBASE_CREDENTIALS'):
            # Cloud deployment: Load from environment variable
            cred_json = json.loads(os.getenv('FIREBASE_CREDENTIALS'))
            cred = credentials.Certificate(cred_json)
        else:
            print("⚠️ Firebase credentials not found. Using SQLite fallback.")
            return None, None
        
        # Initialize app
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', '')
        })
        
        # Get Firestore and Storage clients
        db = firestore.client()
        bucket = storage.bucket()
        
        _firebase_initialized = True
        print("✅ Firebase initialized successfully!")
        return db, bucket
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        print("   Falling back to SQLite")
        return None, None

def get_db():
    """Get Firestore database client"""
    global db
    if db is None:
        db, _ = init_firebase()
    return db

def get_storage():
    """Get Firebase Storage bucket"""
    global bucket
    if bucket is None:
        _, bucket = init_firebase()
    return bucket

# Students Collection Methods
async def create_student(student_data: Dict) -> str:
    """Create a new student in Firestore"""
    db = get_db()
    if db is None:
        raise Exception("Firebase not initialized")
    
    student_id = student_data['student_id']
    student_data['created_at'] = datetime.now()
    student_data['updated_at'] = datetime.now()
    
    db.collection('students').document(student_id).set(student_data)
    return student_id

async def get_student(student_id: str) -> Optional[Dict]:
    """Get a student by ID"""
    db = get_db()
    if db is None:
        return None
    
    doc = db.collection('students').document(student_id).get()
    if doc.exists:
        data = doc.to_dict()
        data['student_id'] = doc.id
        return data
    return None

async def get_all_students(class_name: Optional[str] = None) -> List[Dict]:
    """Get all students, optionally filtered by class"""
    db = get_db()
    if db is None:
        return []
    
    query = db.collection('students')
    
    if class_name:
        query = query.where('class_name', '==', class_name)
    
    docs = query.stream()
    students = []
    for doc in docs:
        data = doc.to_dict()
        data['student_id'] = doc.id
        students.append(data)
    
    return students

async def update_student(student_id: str, updates: Dict) -> bool:
    """Update student information"""
    db = get_db()
    if db is None:
        return False
    
    updates['updated_at'] = datetime.now()
    db.collection('students').document(student_id).update(updates)
    return True

async def delete_student(student_id: str) -> bool:
    """Delete a student"""
    db = get_db()
    if db is None:
        return False
    
    db.collection('students').document(student_id).delete()
    return True

# Attendance Records Collection Methods
async def create_attendance_record(record_data: Dict) -> str:
    """Create a new attendance record"""
    db = get_db()
    if db is None:
        raise Exception("Firebase not initialized")
    
    record_data['timestamp'] = datetime.now()
    doc_ref = db.collection('attendance_records').document()
    doc_ref.set(record_data)
    
    return doc_ref.id

async def get_attendance_record(record_id: str) -> Optional[Dict]:
    """Get an attendance record by ID"""
    db = get_db()
    if db is None:
        return None
    
    doc = db.collection('attendance_records').document(record_id).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

async def get_attendance_records(
    class_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """Get attendance records with optional filters"""
    db = get_db()
    if db is None:
        return []
    
    query = db.collection('attendance_records')
    
    if class_name:
        query = query.where('class_name', '==', class_name)
    
    if start_date:
        query = query.where('date', '>=', start_date)
    
    if end_date:
        query = query.where('date', '<=', end_date)
    
    query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
    
    docs = query.stream()
    records = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        # Convert Firestore timestamp to string
        if 'timestamp' in data and hasattr(data['timestamp'], 'strftime'):
            data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        records.append(data)
    
    return records

async def save_attendance_detail(detail_data: Dict) -> str:
    """Save individual student attendance detail"""
    db = get_db()
    if db is None:
        raise Exception("Firebase not initialized")
    
    doc_ref = db.collection('attendance_details').document()
    doc_ref.set(detail_data)
    
    return doc_ref.id

async def get_attendance_details(attendance_record_id: str) -> List[Dict]:
    """Get all attendance details for a specific record"""
    db = get_db()
    if db is None:
        return []
    
    query = db.collection('attendance_details').where('attendance_record_id', '==', attendance_record_id)
    docs = query.stream()
    
    details = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        details.append(data)
    
    return details

# Storage Methods for Images
async def upload_image(file_path: str, destination_path: str) -> str:
    """Upload an image to Firebase Storage"""
    bucket = get_storage()
    if bucket is None:
        raise Exception("Firebase Storage not initialized")
    
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(file_path)
    
    # Make publicly accessible (optional)
    blob.make_public()
    
    return blob.public_url

async def delete_image(storage_path: str) -> bool:
    """Delete an image from Firebase Storage"""
    bucket = get_storage()
    if bucket is None:
        return False
    
    try:
        blob = bucket.blob(storage_path)
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False

def init_db():
    """Initialize Firebase database (compatibility with existing code)"""
    init_firebase()
    print("Database initialized successfully")

# Export for compatibility
__all__ = [
    'init_firebase',
    'init_db',
    'get_db',
    'get_storage',
    'create_student',
    'get_student',
    'get_all_students',
    'update_student',
    'delete_student',
    'create_attendance_record',
    'get_attendance_record',
    'get_attendance_records',
    'save_attendance_detail',
    'get_attendance_details',
    'upload_image',
    'delete_image',
]
