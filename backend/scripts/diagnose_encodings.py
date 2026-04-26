"""
Diagnostic script to check face encodings and their validity
"""
import sys
import os
import pickle
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_encodings():
    """Check the stored face encodings"""
    encodings_file = "data/encodings/yolov8_face_encodings.pkl"
    
    if not os.path.exists(encodings_file):
        print(f"❌ Encodings file not found: {encodings_file}")
        return
    
    print(f"✅ Found encodings file: {encodings_file}")
    print(f"   File size: {os.path.getsize(encodings_file)} bytes\n")
    
    # Load encodings
    with open(encodings_file, 'rb') as f:
        data = pickle.load(f)
    
    encodings = data.get('encodings', {})
    names = data.get('names', {})
    model = data.get('model', 'unknown')
    distance_metric = data.get('distance_metric', 'unknown')
    
    print(f"Model: {model}")
    print(f"Distance Metric: {distance_metric}")
    print(f"Total Students with Encodings: {len(encodings)}\n")
    
    print("="*80)
    print("STUDENT ENCODINGS DETAILS")
    print("="*80)
    
    for student_id, encoding in encodings.items():
        student_name = names.get(student_id, 'Unknown')
        
        if isinstance(encoding, list):
            print(f"\nStudent ID: {student_id}")
            print(f"Name: {student_name}")
            print(f"Number of encodings: {len(encoding)}")
            for i, enc in enumerate(encoding):
                if isinstance(enc, np.ndarray):
                    print(f"  Encoding {i+1}: shape={enc.shape}, norm={np.linalg.norm(enc):.4f}")
                else:
                    print(f"  Encoding {i+1}: Invalid type - {type(enc)}")
        elif isinstance(encoding, np.ndarray):
            print(f"\nStudent ID: {student_id}")
            print(f"Name: {student_name}")
            print(f"Encoding: shape={encoding.shape}, norm={np.linalg.norm(encoding):.4f}")
            
            # Check if normalized
            norm = np.linalg.norm(encoding)
            if abs(norm - 1.0) < 0.01:
                print(f"  ✅ Encoding is normalized (norm ≈ 1.0)")
            else:
                print(f"  ⚠️  Encoding may not be normalized (norm = {norm:.4f})")
        else:
            print(f"\nStudent ID: {student_id}")
            print(f"Name: {student_name}")
            print(f"❌ Invalid encoding type: {type(encoding)}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total students: {len(encodings)}")
    print(f"Students: {list(names.values())}")

if __name__ == "__main__":
    check_encodings()
