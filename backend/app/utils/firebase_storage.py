"""
Firebase Storage Helper
Automatically uploads and manages images in Firebase Storage
"""

import os
from datetime import datetime
from typing import Optional
from app.models.firebase_database import get_storage, init_firebase

class FirebaseStorageManager:
    """Manages image uploads to Firebase Storage"""
    
    def __init__(self):
        self.bucket = None
        self.use_firebase = os.getenv('USE_FIREBASE', 'false').lower() == 'true'
        
        if self.use_firebase:
            try:
                _, self.bucket = init_firebase()
                print("✅ Firebase Storage Manager initialized")
            except Exception as e:
                print(f"⚠️ Firebase Storage not available: {e}")
                self.bucket = None
    
    async def upload_student_image(self, local_path: str, student_id: str) -> Optional[str]:
        """
        Upload student image to Firebase Storage
        
        Args:
            local_path: Local file path
            student_id: Student ID
            
        Returns:
            Public URL of uploaded image or local path if Firebase unavailable
        """
        if not self.bucket:
            return local_path  # Use local storage if Firebase unavailable
        
        try:
            # Create storage path: students/{student_id}/{filename}
            filename = os.path.basename(local_path)
            storage_path = f"students/{student_id}/{filename}"
            
            # Upload to Firebase
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(local_path)
            
            # Make publicly accessible
            blob.make_public()
            
            url = blob.public_url
            print(f"✅ Uploaded student image to Firebase: {storage_path}")
            
            # Optionally delete local file after upload
            # os.remove(local_path)
            
            return url
            
        except Exception as e:
            print(f"❌ Error uploading to Firebase: {e}")
            return local_path  # Fallback to local path
    
    async def upload_attendance_image(self, local_path: str, class_name: str) -> Optional[str]:
        """
        Upload attendance image to Firebase Storage
        
        Args:
            local_path: Local file path
            class_name: Class name
            
        Returns:
            Public URL of uploaded image or local path if Firebase unavailable
        """
        if not self.bucket:
            return local_path
        
        try:
            # Create storage path: attendance/{class}/{date}/{filename}
            today = datetime.now().strftime("%Y-%m-%d")
            filename = os.path.basename(local_path)
            storage_path = f"attendance/{class_name}/{today}/{filename}"
            
            # Upload to Firebase
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(local_path)
            blob.make_public()
            
            url = blob.public_url
            print(f"✅ Uploaded attendance image to Firebase: {storage_path}")
            
            return url
            
        except Exception as e:
            print(f"❌ Error uploading to Firebase: {e}")
            return local_path
    
    async def delete_image(self, firebase_path: str) -> bool:
        """
        Delete image from Firebase Storage
        
        Args:
            firebase_path: Path in Firebase Storage (e.g., students/123/photo.jpg)
            
        Returns:
            True if deleted successfully
        """
        if not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(firebase_path)
            blob.delete()
            print(f"✅ Deleted from Firebase: {firebase_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting from Firebase: {e}")
            return False
    
    async def get_image_url(self, firebase_path: str) -> Optional[str]:
        """
        Get public URL for an image in Firebase Storage
        
        Args:
            firebase_path: Path in Firebase Storage
            
        Returns:
            Public URL or None
        """
        if not self.bucket:
            return None
        
        try:
            blob = self.bucket.blob(firebase_path)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f"❌ Error getting URL: {e}")
            return None
    
    def list_student_images(self, student_id: str) -> list:
        """
        List all images for a student
        
        Args:
            student_id: Student ID
            
        Returns:
            List of image URLs
        """
        if not self.bucket:
            return []
        
        try:
            prefix = f"students/{student_id}/"
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            urls = []
            for blob in blobs:
                blob.make_public()
                urls.append(blob.public_url)
            
            return urls
        except Exception as e:
            print(f"❌ Error listing images: {e}")
            return []
    
    def list_attendance_images(self, class_name: str, date: str = None) -> list:
        """
        List attendance images for a class
        
        Args:
            class_name: Class name
            date: Date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            List of image URLs
        """
        if not self.bucket:
            return []
        
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            prefix = f"attendance/{class_name}/{date}/"
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            urls = []
            for blob in blobs:
                blob.make_public()
                urls.append(blob.public_url)
            
            return urls
        except Exception as e:
            print(f"❌ Error listing attendance images: {e}")
            return []

# Global instance
storage_manager = FirebaseStorageManager()
