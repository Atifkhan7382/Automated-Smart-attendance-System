"""
Test API Endpoints - Python Script for Windows
Use this to test the backend server with real images
"""

import requests
import os
import json

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test if server is running"""
    print("\n" + "="*60)
    print("TEST: Server Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running!")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("Please start the server with: uvicorn app.main:app --reload")
        return False


def test_student_enrollment(student_id, name, photo_path):
    """Test student enrollment with quality checks"""
    print("\n" + "="*60)
    print(f"TEST: Student Enrollment - {name}")
    print("="*60)
    
    if not os.path.exists(photo_path):
        print(f"❌ Photo not found: {photo_path}")
        return False
    
    try:
        files = {'photo': open(photo_path, 'rb')}
        data = {
            'student_id': student_id,
            'name': name
        }
        
        response = requests.post(
            f"{BASE_URL}/api/students/enroll",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print(f"✅ Enrollment successful!")
            result = response.json()
            print(f"Student ID: {result.get('student_id')}")
            print(f"Name: {result.get('name')}")
            print(f"Encoding generated: {result.get('encoding_generated', False)}")
            return True
        else:
            print(f"❌ Enrollment failed (Status {response.status_code})")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_manual_attendance(class_name, image_path):
    """Test manual attendance with quality validation"""
    print("\n" + "="*60)
    print(f"TEST: Manual Attendance - {class_name}")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    try:
        files = {'file': open(image_path, 'rb')}
        data = {'class_name': class_name}
        
        response = requests.post(
            f"{BASE_URL}/api/attendance/mark",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print(f"✅ Attendance marked successfully!")
            result = response.json()
            print(f"Present: {len(result.get('present', []))} students")
            print(f"Absent: {len(result.get('absent', []))} students")
            print(f"Faces detected: {result.get('total_faces_detected', 0)}")
            print(f"Attendance %: {result.get('attendance_percentage', 0):.1f}%")
            return True
        elif response.status_code == 422:
            print(f"❌ Image quality too low (HTTP 422)")
            error = response.json()
            detail = error.get('detail', {})
            print(f"\nError: {detail.get('error', 'Unknown')}")
            print(f"Message: {detail.get('message', '')}")
            
            issues = detail.get('issues', [])
            if issues:
                print(f"\nQuality Issues:")
                for issue in issues:
                    print(f"  - {issue}")
            
            suggestions = detail.get('suggestions', [])
            if suggestions:
                print(f"\nSuggestions:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
            return False
        else:
            print(f"❌ Request failed (Status {response.status_code})")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("BACKEND API TESTING - Real Image Tests")
    print("="*60)
    
    # Test 1: Server health
    if not test_server_health():
        print("\n⚠️  Server is not running. Please start it first.")
        return
    
    print("\n" + "="*60)
    print("INSTRUCTIONS FOR TESTING")
    print("="*60)
    print("""
To test with real images, you need to:

1. STUDENT ENROLLMENT TEST:
   - Place a student photo in the backend folder
   - Run: test_student_enrollment('student_001', 'John Doe', 'photo.jpg')
   
2. MANUAL ATTENDANCE TEST:
   - Place a classroom photo in the backend folder
   - Run: test_manual_attendance('CS101', 'classroom.jpg')

EXAMPLE USAGE:
--------------
# Test enrollment with a good quality photo
test_student_enrollment('test_001', 'Test Student', 'good_photo.jpg')

# Test enrollment with a poor quality photo (should reject)
test_student_enrollment('test_002', 'Bad Photo', 'blurry_photo.jpg')

# Test attendance with classroom image
test_manual_attendance('CS101', 'classroom.jpg')

EXPECTED RESULTS:
-----------------
✅ Good quality photos: Accepted
❌ Blurry photos: Rejected with "Image is blurry"
❌ Eyes closed: Rejected with "Eyes are closed"
❌ Non-frontal: Rejected with "Face is not frontal"
❌ Wearing mask: Rejected with "Face is occluded"
    """)


if __name__ == "__main__":
    main()
