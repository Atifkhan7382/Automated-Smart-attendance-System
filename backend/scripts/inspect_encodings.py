"""
Inspect face encodings to debug attendance accuracy
"""
import pickle
import os

encodings_file = "data/encodings/yolov8_face_encodings.pkl"

if os.path.exists(encodings_file):
    with open(encodings_file, 'rb') as f:
        data = pickle.load(f)
    
    print("=" * 70)
    print("FACE ENCODINGS INSPECTION")
    print("=" * 70)
    
    if isinstance(data, dict):
        print(f"\nTotal students with encodings: {len(data)}")
        print("\nStudent IDs and encoding counts:")
        for student_id, encodings in data.items():
            if isinstance(encodings, list):
                print(f"  - {student_id}: {len(encodings)} encoding(s)")
            else:
                print(f"  - {student_id}: 1 encoding")
    else:
        print(f"\nData type: {type(data)}")
        print(f"Data: {data}")
else:
    print(f"❌ Encodings file not found: {encodings_file}")

# Also check the database for enrolled students
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.database import DatabaseManager

print("\n" + "=" * 70)
print("DATABASE STUDENTS")
print("=" * 70)

students = DatabaseManager.execute_query(
    "SELECT student_id, name, class_name, image_path FROM students"
)

if students:
    print(f"\nTotal students in database: {len(students)}")
    for student in students:
        print(f"  - {student['student_id']}: {student['name']} (Class: {student['class_name']})")
        print(f"    Video: {student.get('image_path', 'None')}")
else:
    print("No students found in database")
