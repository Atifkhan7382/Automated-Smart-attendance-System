"""
Delete Student Data Script
Removes student videos, images, and face encodings for specified students
"""
import sqlite3
import os
import shutil
import sys
from typing import List, Optional

def get_db_path():
    """Get the correct database path regardless of where script is run from"""
    # Try backend/data/attendance.db first
    if os.path.exists("data/attendance.db"):
        return "data/attendance.db"
    # Try from parent directory
    elif os.path.exists("backend/data/attendance.db"):
        return "backend/data/attendance.db"
    else:
        raise FileNotFoundError("Could not find attendance.db. Please run from backend/ or project root directory.")

def get_data_dir():
    """Get the correct data directory path"""
    if os.path.exists("data"):
        return "data"
    elif os.path.exists("backend/data"):
        return "backend/data"
    else:
        raise FileNotFoundError("Could not find data directory.")

def get_all_students():
    """Get list of all students from database"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT student_id, name, class_name, image_path 
        FROM students 
        ORDER BY name
    """)
    students = cursor.fetchall()
    conn.close()
    
    return students

def delete_student_data(student_id: str, verbose: bool = True):
    """
    Delete all data for a specific student
    
    Args:
        student_id: The student ID to delete data for
        verbose: Print detailed information
    """
    if verbose:
        print(f"\n🗑️  Deleting data for student: {student_id}")
    
    data_dir = get_data_dir()
    
    # Delete student videos directory
    video_dir = f"{data_dir}/student_videos/{student_id}"
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
        if verbose:
            print(f"   ✅ Deleted videos: {video_dir}")
    
    # Delete student images directory
    image_dir = f"{data_dir}/student_images/{student_id}"
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)
        if verbose:
            print(f"   ✅ Deleted images: {image_dir}")
    
    # Clear image path in database
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE students SET image_path = NULL, updated_at = CURRENT_TIMESTAMP WHERE student_id = ?",
        (student_id,)
    )
    
    conn.commit()
    conn.close()
    
    if verbose:
        print(f"   ✅ Cleared database image path")
    
    # Note: Face encodings will be removed when the service reloads
    if verbose:
        print(f"   ℹ️  Face encodings will be removed on next service reload")

def delete_all_student_data(confirm: bool = False):
    """Delete data for ALL students"""
    if not confirm:
        print("⚠️  WARNING: This will delete ALL student data!")
        response = input("Type 'DELETE ALL' to confirm: ")
        if response != "DELETE ALL":
            print("❌ Cancelled")
            return
    
    students = get_all_students()
    
    if not students:
        print("ℹ️  No students found in database")
        return
    
    print(f"\n🗑️  Deleting data for {len(students)} students...")
    
    for student_id, name, class_name, image_path in students:
        delete_student_data(student_id, verbose=False)
        print(f"   ✅ {name} ({student_id})")
    
    print(f"\n✅ Deleted data for {len(students)} students")

def delete_students_by_class(class_name: str):
    """Delete data for all students in a specific class"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT student_id, name FROM students WHERE class_name = ?",
        (class_name,)
    )
    students = cursor.fetchall()
    conn.close()
    
    if not students:
        print(f"ℹ️  No students found in class: {class_name}")
        return
    
    print(f"\n⚠️  Found {len(students)} students in class '{class_name}':")
    for student_id, name in students:
        print(f"   - {name} ({student_id})")
    
    response = input(f"\nDelete data for all {len(students)} students? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    print(f"\n🗑️  Deleting data for students in class '{class_name}'...")
    
    for student_id, name in students:
        delete_student_data(student_id, verbose=False)
        print(f"   ✅ {name} ({student_id})")
    
    print(f"\n✅ Deleted data for {len(students)} students")

def list_students():
    """List all students with their data status"""
    students = get_all_students()
    
    if not students:
        print("ℹ️  No students found in database")
        return
    
    print("\n📊 Student Data Status:")
    print("="*80)
    print(f"{'Student ID':<15} {'Name':<20} {'Class':<15} {'Has Data':<10}")
    print("-"*80)
    
    for student_id, name, class_name, image_path in students:
        has_data = "Yes" if image_path else "No"
        print(f"{student_id:<15} {name:<20} {class_name or 'Unassigned':<15} {has_data:<10}")
    
    print("="*80)
    print(f"Total students: {len(students)}")

def interactive_mode():
    """Interactive menu for deleting student data"""
    while True:
        print("\n" + "="*60)
        print("DELETE STUDENT DATA - Interactive Mode")
        print("="*60)
        print("\nOptions:")
        print("1. List all students")
        print("2. Delete data for specific student")
        print("3. Delete data for all students in a class")
        print("4. Delete data for ALL students")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            list_students()
        
        elif choice == "2":
            list_students()
            student_id = input("\nEnter student ID to delete: ").strip()
            if student_id:
                confirm = input(f"Delete data for student '{student_id}'? (yes/no): ")
                if confirm.lower() == 'yes':
                    delete_student_data(student_id)
                    print("\n✅ Student data deleted successfully")
                else:
                    print("❌ Cancelled")
        
        elif choice == "3":
            class_name = input("\nEnter class name: ").strip()
            if class_name:
                delete_students_by_class(class_name)
        
        elif choice == "4":
            delete_all_student_data()
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def main():
    """Main function"""
    print("="*60)
    print("DELETE STUDENT DATA SCRIPT")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_students()
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("❌ Usage: python delete_student_data.py delete <student_id>")
                return
            student_id = sys.argv[2]
            delete_student_data(student_id)
        
        elif command == "delete-class":
            if len(sys.argv) < 3:
                print("❌ Usage: python delete_student_data.py delete-class <class_name>")
                return
            class_name = sys.argv[2]
            delete_students_by_class(class_name)
        
        elif command == "delete-all":
            delete_all_student_data()
        
        elif command == "help":
            print("\nUsage:")
            print("  python delete_student_data.py                    # Interactive mode")
            print("  python delete_student_data.py list               # List all students")
            print("  python delete_student_data.py delete <id>        # Delete specific student")
            print("  python delete_student_data.py delete-class <cls> # Delete class students")
            print("  python delete_student_data.py delete-all         # Delete all students")
            print("  python delete_student_data.py help               # Show this help")
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python delete_student_data.py help' for usage")
    
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
