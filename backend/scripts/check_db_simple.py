"""
Simple database check
"""
import sqlite3

conn = sqlite3.connect("data/attendance.db")
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])
print()

# Get students
cursor.execute("SELECT * FROM students LIMIT 10")
students = cursor.fetchall()

# Get column names
cursor.execute("PRAGMA table_info(students)")
columns = cursor.fetchall()
print("Students table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")
print()

print("Students:")
for s in students:
    print(s)

conn.close()
