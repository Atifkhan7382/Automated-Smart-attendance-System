import sqlite3
import os

# Find the database
db_path = "data/attendance.db" if os.path.exists("data/attendance.db") else "app/data/attendance.db"

print(f"Checking database at: {db_path}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check classes table
print("\n=== Classes with invite codes ===")
cursor.execute("SELECT id, class_name, invite_code, invite_expires_at FROM classes")
classes = cursor.fetchall()

if not classes:
    print("No classes found in database")
else:
    for cls in classes:
        print(f"ID: {cls['id']}, Name: {cls['class_name']}, Invite Code: {cls['invite_code']}, Expires: {cls['invite_expires_at']}")

# Check if there are any classes at all
cursor.execute("SELECT COUNT(*) as count FROM classes")
count = cursor.fetchone()['count']
print(f"\nTotal classes in database: {count}")

conn.close()
