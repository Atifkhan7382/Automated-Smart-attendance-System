import sqlite3

conn = sqlite3.connect('data/attendance.db')
cursor = conn.cursor()

# Get the schema for attendance_verifications table
cursor.execute("PRAGMA table_info(attendance_verifications)")
columns = cursor.fetchall()

print("attendance_verifications table structure:")
print("-" * 80)
print(f"{'Column':<30} {'Type':<15} {'Not Null':<10} {'Default':<15} {'PK'}")
print("-" * 80)

for col in columns:
    cid, name, col_type, notnull, default_val, pk = col
    print(f"{name:<30} {col_type:<15} {str(bool(notnull)):<10} {str(default_val):<15} {bool(pk)}")

# Get foreign key info
cursor.execute("PRAGMA foreign_key_list(attendance_verifications)")
fks = cursor.fetchall()

if fks:
    print("\n\nForeign Keys:")
    print("-" * 80)
    for fk in fks:
        print(f"  {fk[3]} -> {fk[2]}({fk[4]})")

conn.close()
