"""
Quick Database Inspector
Shows all tables and their row counts
"""
import sqlite3

db_path = "data/attendance.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE INSPECTION")
print("=" * 60)
print(f"\nDatabase: {db_path}\n")

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Total Tables: {len(tables)}\n")

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"📊 {table_name}: {count} rows")

print("\n" + "=" * 60)
print("\nTo view specific table data, use:")
print("  python -c \"import sqlite3; conn = sqlite3.connect('data/attendance.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM table_name LIMIT 10'); [print(row) for row in cursor.fetchall()]\"")
print("=" * 60)

conn.close()
