import sqlite3

def get_schema():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(employees)")
    return cursor.fetchall()
