import pickle
import os
import json

print("=" * 80)
print("FACE ENCODINGS DIAGNOSTIC")
print("=" * 80)

# Check encodings file
encodings_file = "data/encodings/yolov8_face_encodings.pkl"
print(f"\nEncodings file: {encodings_file}")
print(f"Exists: {os.path.exists(encodings_file)}")

if os.path.exists(encodings_file):
    with open(encodings_file, 'rb') as f:
        data = pickle.load(f)
    
    print(f"Data type: {type(data)}")
    print(f"Number of students: {len(data)}")
    
    for student_id, encodings in data.items():
        if isinstance(encodings, list):
            print(f"  Student {student_id}: {len(encodings)} encodings")
        else:
            print(f"  Student {student_id}: 1 encoding")

# Check settings
settings_file = "data/app_settings.json"
print(f"\nSettings file: {settings_file}")
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    print(f"InsightFace similarity threshold: {settings.get('insightfaceRecognition', {}).get('similarityThreshold')}")
    print(f"Detection confidence: {settings.get('yolov8Detection', {}).get('confidence')}")
