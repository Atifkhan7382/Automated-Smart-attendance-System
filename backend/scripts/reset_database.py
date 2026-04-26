"""
Database Reset Script
Clears all data and starts fresh while preserving schema
"""
import sqlite3
import os
import shutil
from datetime import datetime

def backup_database():
    """Create backup of current database"""
    db_path = "data/attendance.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backups/attendance_backup_{timestamp}.db"
        os.makedirs("data/backups", exist_ok=True)
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    return None

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
        print(f"   Cleared: {table_name}")
    
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
    
    for dir_path in directories:
        if os.path.exists(dir_path):
            # Remove all contents but keep the directory
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(f"✅ Cleared: {dir_path}")

def verify_reset():
    """Verify database is empty"""
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    
    print("\n📊 Verification:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   {table_name}: {count} records")
    
    conn.close()

def main():
    """Main reset function"""
    print("="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60)
    
    # Confirm action
    print("\n⚠️  WARNING: This will delete ALL data!")
    print("   - All users (teachers and students)")
    print("   - All classes and enrollments")
    print("   - All attendance records")
    print("   - All face encodings")
    print("   - All student images/videos")
    
    confirm = input("\nType 'RESET' to confirm: ")
    if confirm != "RESET":
        print("❌ Reset cancelled")
        return
    
    # Create backup
    backup_path = backup_database()
    
    # Clear everything
    clear_database()
    clear_face_encodings()
    clear_student_data()
    
    # Verify
    verify_reset()
    
    print("\n" + "="*60)
    print("✅ DATABASE RESET COMPLETE")
    print("="*60)
    if backup_path:
        print(f"\n💾 Backup saved at: {backup_path}")
    print("\n🚀 You can now start fresh with a clean system!")

if __name__ == "__main__":
    main()
