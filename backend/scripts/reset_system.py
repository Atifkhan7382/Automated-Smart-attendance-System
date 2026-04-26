"""
Complete System Reset Script
Clears all student data, photos, videos, encodings, and user accounts
Keeps only the database structure and teacher accounts
"""
import os
import shutil
import sqlite3
from pathlib import Path

def reset_system():
    print("🔄 Starting complete system reset...")
    print("=" * 60)
    
    # 1. Clear all image and video directories
    directories_to_clear = [
        'data/student_images',
        'data/student_videos',
        'data/attendance_images',
        'data/encodings'
    ]
    
    for directory in directories_to_clear:
        if os.path.exists(directory):
            try:
                # Remove all files in directory
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"  ✅ Deleted file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"  ✅ Deleted directory: {item_path}")
                print(f"✅ Cleared: {directory}")
            except Exception as e:
                print(f"❌ Error clearing {directory}: {e}")
        else:
            print(f"⚠️  Directory not found: {directory}")
    
    # 2. Reset database - keep structure, clear data
    db_path = 'data/attendance.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get counts before deletion
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
            student_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'")
            teacher_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM students")
            students = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM classes")
            classes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM attendance_records")
            attendance = cursor.fetchone()[0]
            
            print(f"\n📊 Current Database Status:")
            print(f"  - Teacher accounts: {teacher_users}")
            print(f"  - Student accounts: {student_users}")
            print(f"  - Student records: {students}")
            print(f"  - Classes: {classes}")
            print(f"  - Attendance records: {attendance}")
            
            # Delete all student-related data
            print(f"\n🗑️  Deleting data...")
            
            cursor.execute("DELETE FROM student_attendance")
            print(f"  ✅ Cleared student_attendance table")
            
            cursor.execute("DELETE FROM attendance_records")
            print(f"  ✅ Cleared attendance_records table")
            
            cursor.execute("DELETE FROM class_enrollments")
            print(f"  ✅ Cleared class_enrollments table")
            
            cursor.execute("DELETE FROM students")
            print(f"  ✅ Cleared students table")
            
            cursor.execute("DELETE FROM classes")
            print(f"  ✅ Cleared classes table")
            
            cursor.execute("DELETE FROM users WHERE role = 'student'")
            print(f"  ✅ Deleted {student_users} student user accounts")
            
            # Optional: Also delete teacher accounts (uncomment if needed)
            # cursor.execute("DELETE FROM users WHERE role = 'teacher'")
            # print(f"  ✅ Deleted {teacher_users} teacher user accounts")
            
            conn.commit()
            
            # Verify deletion
            cursor.execute("SELECT COUNT(*) FROM users")
            remaining_users = cursor.fetchone()[0]
            
            print(f"\n✅ Database reset complete!")
            print(f"  - Remaining user accounts: {remaining_users} (teachers)")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️  Database not found: {db_path}")
    
    print("\n" + "=" * 60)
    print("✨ System reset complete!")
    print("\n📝 Next steps:")
    print("1. Restart the backend server")
    print("2. Teacher accounts are preserved (if any)")
    print("3. Register new teacher (or use existing)")
    print("4. Create classes and generate invite links")
    print("5. Students register using invite links")
    print("6. Students upload face recognition videos")
    print("7. Mark attendance!")

if __name__ == "__main__":
    confirm = input("\n⚠️  WARNING: This will delete ALL student data, photos, videos, and encodings!\n"
                   "Teacher accounts will be preserved.\n"
                   "Type 'RESET' to confirm: ")
    
    if confirm == "RESET":
        reset_system()
    else:
        print("❌ Reset cancelled.")
