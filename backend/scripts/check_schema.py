import sqlite3

conn = sqlite3.connect("data/attendance.db")
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(students)")
cols = cursor.fetchall()

print("Students table schema:")
print("="*60)
for col in cols:
    col_id, name, type_, notnull, default, pk = col
    null_str = "NOT NULL" if notnull else "NULL"
    default_str = f" DEFAULT {default}" if default else ""
    pk_str = " PRIMARY KEY" if pk else ""
    print(f"{name}: {type_} {null_str}{default_str}{pk_str}")

conn.close()
