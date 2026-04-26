"""
Script to clear old student data and face encodings
This will allow you to start fresh with new student videos
"""
import os
import shutil
import sqlite3

def clear_student_data():
    print("🧹 Clearing old student data and face encodings...")
    
    # 1. Clear face encoding files
    encoding_files = [
        'data/encodings/face_encodings.pkl',
        'data/encodings/yolov8_face_encodings.pkl'
    ]
    
    for file_path in encoding_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Deleted: {file_path}")
    
    # 2. Clear student images
    student_images_dir = 'data/student_images'
    if os.path.exists(student_images_dir):
        for file in os.listdir(student_images_dir):
            file_path = os.path.join(student_images_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"✅ Cleared all files in: {student_images_dir}")
    
    # 3. Clear student videos
    student_videos_dir = 'data/student_videos'
    if os.path.exists(student_videos_dir):
        for file in os.listdir(student_videos_dir):
            file_path = os.path.join(student_videos_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"✅ Cleared all files in: {student_videos_dir}")
    
    # 4. Clear old students from database (keep users for authentication)
    conn = sqlite3.connect('data/attendance.db')
    cursor = conn.cursor()
    
    # Get count before deletion
    cursor.execute("SELECT COUNT(*) FROM students")
    old_count = cursor.fetchone()[0]
    
    # Delete old students (this will cascade to attendance records)
    cursor.execute("DELETE FROM students")
    
    # Clear attendance records
    cursor.execute("DELETE FROM attendance_records")
    cursor.execute("DELETE FROM student_attendance")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {old_count} old student records from database")
    print(f"✅ Cleared all attendance records")
    
    print("\n✨ Database cleared successfully!")
    print("\n📝 Next steps:")
    print("1. Restart the backend server (Ctrl+C and run again)")
    print("2. Login as student")
    print("3. Go to Student Dashboard → Manage Video")
    print("4. Upload a clear 5-10 second video of your face")
    print("5. Repeat for all students")
    print("6. Then try marking attendance again")

if __name__ == "__main__":
    try:
        clear_student_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
