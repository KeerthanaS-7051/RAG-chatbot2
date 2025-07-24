import sqlite3

def query_employee_db(sql: str):
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        return str(e)
