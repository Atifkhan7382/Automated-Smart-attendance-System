"""
Quick Database Reset Script (No Backup)
Clears all data immediately
"""
import sqlite3
import os
import shutil

def clear_database():
    """Clear all tables in the database"""
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print("\n🗑️  Clearing database tables...")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DELETE FROM {table_name}")
        print(f"   ✅ Cleared: {table_name}")
    
    # Reset auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    print("✅ Database cleared successfully\n")

def clear_face_encodings():
    """Clear face encodings file"""
    encodings_file = "data/encodings/yolov8_face_encodings.pkl"
    if os.path.exists(encodings_file):
        os.remove(encodings_file)
        print("✅ Face encodings cleared")

def clear_student_data():
    """Clear student images and videos"""
    directories = [
        "data/student_images",
        "data/student_videos",
        "data/attendance_images"
    ]
    
    print("\n🗑️  Clearing student data...")
    for dir_path in directories:
        if os.path.exists(dir_path):
            # Remove all contents but keep the directory
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"   ⚠️  Could not remove {item}: {e}")
            print(f"   ✅ Cleared: {dir_path}")

def verify_reset():
    """Verify database is empty"""
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    
    print("\n📊 Verification:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    all_empty = True
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        status = "✅" if count == 0 else "❌"
        print(f"   {status} {table_name}: {count} records")
        if count > 0:
            all_empty = False
    
    conn.close()
    return all_empty

def main():
    """Main reset function"""
    print("="*60)
    print("DATABASE RESET")
    print("="*60)
    
    # Clear everything
    clear_database()
    clear_face_encodings()
    clear_student_data()
    
    # Verify
    success = verify_reset()
    
    print("\n" + "="*60)
    if success:
        print("✅ DATABASE RESET COMPLETE")
        print("="*60)
        print("\n🚀 System is now clean and ready for fresh start!")
    else:
        print("⚠️  RESET INCOMPLETE - Some data remains")
        print("="*60)

if __name__ == "__main__":
    main()
