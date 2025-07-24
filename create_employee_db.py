import sqlite3

conn = sqlite3.connect("employee.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS employee")

cursor.execute("""
CREATE TABLE employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL
)
""")

sample_data = [
    ("Alice", "HR", 50000),
    ("Bob", "Engineering", 70000),
    ("Charlie", "Marketing", 60000),
    ("David", "Engineering", 75000),
    ("Eva", "HR", 52000),
]

cursor.executemany("INSERT INTO employee (name, department, salary) VALUES (?, ?, ?)", sample_data)

conn.commit()
conn.close()

print("employee.db created with sample data.")
