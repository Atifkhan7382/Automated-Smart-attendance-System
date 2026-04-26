"""
Generate invite codes for existing classes that don't have them
"""
import sqlite3
import secrets
import string

def generate_invite_code():
    """Generate a random 12-character invite code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))

db_path = "data/attendance.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all classes without invite codes
cursor.execute("SELECT id, class_name FROM classes WHERE invite_code IS NULL")
classes = cursor.fetchall()

print(f"Found {len(classes)} classes without invite codes")
print("-" * 60)

for class_id, class_name in classes:
    invite_code = generate_invite_code()
    cursor.execute(
        "UPDATE classes SET invite_code = ? WHERE id = ?",
        (invite_code, class_id)
    )
    print(f"✓ Generated code for '{class_name}': {invite_code}")

conn.commit()
conn.close()

print("-" * 60)
print(f"✅ Updated {len(classes)} classes with invite codes")
