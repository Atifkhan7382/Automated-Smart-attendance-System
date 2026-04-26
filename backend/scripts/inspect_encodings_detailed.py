import pickle
import os
import numpy as np

encodings_file = "data/encodings/yolov8_face_encodings.pkl"

print("="*80)
print("DETAILED ENCODINGS INSPECTION")
print("="*80)

if os.path.exists(encodings_file):
    with open(encodings_file, 'rb') as f:
        data = pickle.load(f)
    
    print(f"\nPickle file structure:")
    print(f"Type: {type(data)}")
    print(f"Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
    
    if isinstance(data, dict):
        encodings = data.get('encodings', {})
        names = data.get('names', {})
        
        print(f"\nEncodings dict:")
        print(f"  Type: {type(encodings)}")
        print(f"  Number of students: {len(encodings)}")
        
        for student_id, encoding in encodings.items():
            print(f"\n  Student ID: {student_id}")
            print(f"    Name: {names.get(student_id, 'Unknown')}")
            print(f"    Encoding type: {type(encoding)}")
            if isinstance(encoding, np.ndarray):
                print(f"    Encoding shape: {encoding.shape}")
                print(f"    Encoding norm: {np.linalg.norm(encoding):.4f}")
            elif isinstance(encoding, list):
                print(f"    Number of encodings: {len(encoding)}")
                if encoding:
                    print(f"    First encoding type: {type(encoding[0])}")
                    if isinstance(encoding[0], np.ndarray):
                        print(f"    First encoding shape: {encoding[0].shape}")
else:
    print(f"File not found: {encodings_file}")
