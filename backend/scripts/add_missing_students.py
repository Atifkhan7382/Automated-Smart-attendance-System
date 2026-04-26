"""
Add missing students to database based on image folders
"""

import sqlite3
import os

# Connect to database
conn = sqlite3.connect('data/attendance.db')
cur = conn.cursor()

# Get existing students
existing = cur.execute('SELECT student_id FROM students').fetchall()
existing_ids = {str(s[0]) for s in existing}

print("Existing students:", existing_ids)

# Get student folders
image_dir = 'data/student_images'
folder_ids = [d for d in os.listdir(image_dir) 
              if os.path.isdir(os.path.join(image_dir, d)) and d.isdigit()]

print("Students with images:", folder_ids)

# Find missing students
missing_ids = [sid for sid in folder_ids if sid not in existing_ids]

print(f"\nMissing students: {missing_ids}")

if missing_ids:
    print("\nAdding missing students to database...")
    class_name = "AIDS"
    
    for student_id in missing_ids:
        # Create a placeholder name (can be updated later)
        name = f"Student_{student_id}"
        
        cur.execute('''
            INSERT INTO students (student_id, name, class_name)
            VALUES (?, ?, ?)
        ''', (int(student_id), name, class_name))
        
        print(f"  ✅ Added student {student_id}: {name}")
    
    conn.commit()
    print(f"\n✅ Added {len(missing_ids)} students to database")
else:
    print("\n✅ All students with images are in the database")

conn.close()
