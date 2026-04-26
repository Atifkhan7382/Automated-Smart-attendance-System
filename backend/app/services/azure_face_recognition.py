"""
Azure Face API Integration for Cloud Face Recognition
Provides accurate face identification without compilation requirements
"""

import os
import requests
import base64
from typing import Dict, List, Optional
import json

class AzureFaceRecognition:
    """Azure Face API service for cloud face recognition"""
    
    def __init__(self):
        # Azure Face API credentials
        self.api_key = os.getenv('AZURE_FACE_API_KEY', '3XjRo4npTKW5umFQXaP5U66EkqguE1X3kjMe5hXhb2fKaUfsaqbPJQQJ99BKACYeBjFXJ3w3AAAKACOGboHu')
        self.endpoint = os.getenv('AZURE_FACE_ENDPOINT', 'https://eastus.api.cognitive.microsoft.com/')
        
        # Azure Face API endpoints
        self.detect_url = f"{self.endpoint}face/v1.0/detect"
        self.person_group_id = "smart-attendance-students"
        
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Content-Type': 'application/octet-stream'
        }
        
        self.available = bool(self.api_key and self.endpoint)
        
        if self.available:
            print("✅ Azure Face API initialized")
        else:
            print("⚠️ Azure Face API not configured")
    
    async def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect faces in an image using Azure Face API
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of detected faces with bounding boxes and face IDs
        """
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Call Azure Face API
            params = {
                'returnFaceId': 'true',
                'returnFaceLandmarks': 'false',
                'returnFaceAttributes': 'age,gender,emotion'
            }
            
            response = requests.post(
                self.detect_url,
                headers=self.headers,
                params=params,
                data=image_data,
                timeout=30
            )
            
            if response.status_code == 200:
                faces = response.json()
                print(f"✅ Azure detected {len(faces)} faces")
                return faces
            else:
                print(f"❌ Azure Face API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error detecting faces with Azure: {e}")
            return []
    
    async def create_person_group(self, student_service):
        """
        Create a person group for storing student faces
        
        Args:
            student_service: StudentManagementService instance
        """
        try:
            url = f"{self.endpoint}face/v1.0/persongroups/{self.person_group_id}"
            
            # Check if person group exists
            response = requests.get(url, headers={'Ocp-Apim-Subscription-Key': self.api_key})
            
            if response.status_code == 404:
                # Create new person group
                data = {
                    'name': 'Smart Attendance Students',
                    'userData': 'Student faces for attendance system'
                }
                
                response = requests.put(
                    url,
                    headers={
                        'Ocp-Apim-Subscription-Key': self.api_key,
                        'Content-Type': 'application/json'
                    },
                    json=data
                )
                
                if response.status_code in [200, 201]:
                    print("✅ Created Azure person group")
                else:
                    print(f"⚠️ Could not create person group: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error creating person group: {e}")
    
    async def add_student_face(self, student_id: str, student_name: str, image_path: str) -> bool:
        """
        Add a student's face to Azure Face API
        
        Args:
            student_id: Student ID
            student_name: Student name
            image_path: Path to student's image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create person in person group
            person_url = f"{self.endpoint}face/v1.0/persongroups/{self.person_group_id}/persons"
            
            person_data = {
                'name': student_name,
                'userData': student_id
            }
            
            response = requests.post(
                person_url,
                headers={
                    'Ocp-Apim-Subscription-Key': self.api_key,
                    'Content-Type': 'application/json'
                },
                json=person_data
            )
            
            if response.status_code != 200:
                print(f"⚠️ Could not create person: {response.text}")
                return False
            
            person_id = response.json()['personId']
            
            # Add face to person
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            face_url = f"{person_url}/{person_id}/persistedFaces"
            
            response = requests.post(
                face_url,
                headers=self.headers,
                data=image_data
            )
            
            if response.status_code == 200:
                print(f"✅ Added face for {student_name}")
                return True
            else:
                print(f"⚠️ Could not add face: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding student face: {e}")
            return False
    
    async def train_person_group(self):
        """Train the person group with all added faces"""
        try:
            url = f"{self.endpoint}face/v1.0/persongroups/{self.person_group_id}/train"
            
            response = requests.post(
                url,
                headers={'Ocp-Apim-Subscription-Key': self.api_key}
            )
            
            if response.status_code == 202:
                print("✅ Training Azure person group...")
                return True
            else:
                print(f"⚠️ Training failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error training person group: {e}")
            return False
    
    async def identify_faces(self, face_ids: List[str]) -> List[Dict]:
        """
        Identify faces using Azure Face API
        
        Args:
            face_ids: List of face IDs from detect_faces()
            
        Returns:
            List of identification results
        """
        try:
            url = f"{self.endpoint}face/v1.0/identify"
            
            data = {
                'personGroupId': self.person_group_id,
                'faceIds': face_ids,
                'maxNumOfCandidatesReturned': 1,
                'confidenceThreshold': 0.5
            }
            
            response = requests.post(
                url,
                headers={
                    'Ocp-Apim-Subscription-Key': self.api_key,
                    'Content-Type': 'application/json'
                },
                json=data
            )
            
            if response.status_code == 200:
                results = response.json()
                return results
            else:
                print(f"⚠️ Identification failed: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error identifying faces: {e}")
            return []
    
    async def process_attendance(self, image_path: str, class_name: str, student_service) -> Dict:
        """
        Process attendance using Azure Face API
        
        Args:
            image_path: Path to classroom image
            class_name: Class name
            student_service: StudentManagementService instance
            
        Returns:
            Attendance results with present and absent students
        """
        try:
            # Detect faces in image
            detected_faces = await self.detect_faces(image_path)
            
            if not detected_faces:
                # No faces detected
                all_students = await student_service.get_students(class_name)
                return {
                    'present': [],
                    'absent': [{'student_id': s['student_id'], 'name': s['name']} for s in all_students],
                    'total_faces_detected': 0,
                    'recognition_method': 'azure_face_api'
                }
            
            # Extract face IDs
            face_ids = [face['faceId'] for face in detected_faces]
            
            # Identify faces
            identification_results = await self.identify_faces(face_ids)
            
            # Get all students in class
            all_students = await student_service.get_students(class_name)
            student_map = {s['student_id']: s for s in all_students}
            
            # Map person IDs to student IDs
            present_student_ids = set()
            present = []
            
            for result in identification_results:
                if result.get('candidates'):
                    # Get person ID
                    person_id = result['candidates'][0]['personId']
                    confidence = result['candidates'][0]['confidence']
                    
                    # Get person details to find student_id
                    person_url = f"{self.endpoint}face/v1.0/persongroups/{self.person_group_id}/persons/{person_id}"
                    response = requests.get(
                        person_url,
                        headers={'Ocp-Apim-Subscription-Key': self.api_key}
                    )
                    
                    if response.status_code == 200:
                        person_data = response.json()
                        student_id = person_data.get('userData', '')
                        
                        if student_id in student_map:
                            present_student_ids.add(student_id)
                            present.append({
                                'student_id': student_id,
                                'name': student_map[student_id]['name'],
                                'confidence': round(confidence, 2)
                            })
            
            # Mark remaining students as absent
            absent = [
                {'student_id': s['student_id'], 'name': s['name']}
                for s in all_students
                if s['student_id'] not in present_student_ids
            ]
            
            print(f"✅ Azure Face API: {len(present)} present, {len(absent)} absent")
            
            return {
                'present': present,
                'absent': absent,
                'total_faces_detected': len(detected_faces),
                'recognition_method': 'azure_face_api'
            }
            
        except Exception as e:
            print(f"❌ Error processing attendance with Azure: {e}")
            # Return all absent on error
            all_students = await student_service.get_students(class_name)
            return {
                'present': [],
                'absent': [{'student_id': s['student_id'], 'name': s['name']} for s in all_students],
                'total_faces_detected': 0,
                'error': str(e)
            }

# Global instance
azure_face_service = AzureFaceRecognition()
