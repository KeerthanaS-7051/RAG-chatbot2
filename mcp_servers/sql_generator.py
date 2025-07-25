import os
import requests
import sqlite3
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from session_store import save_question, get_history
import sqlparse

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

class QueryInput(BaseModel):
    question: str
    session_id: str

def get_schema_and_rows():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(employee)")
    schema = "\n".join([f"{col[1]} ({col[2]})" for col in cursor.fetchall()])

    cursor.execute("SELECT * FROM employee LIMIT 5")
    rows = cursor.fetchall()
    examples = "\n".join([str(row) for row in rows])

    conn.close()
    return schema, examples

def generate_sql(user_input: str, history: list = []) -> str:
    schema, sample_rows = get_schema_and_rows()

    examples = """
Q: Show all employee names.
A: SELECT name FROM employee;

Q: How many employees are there?
A: SELECT COUNT(*) FROM employee;

Q: What is the average salary?
A: SELECT AVG(salary) FROM employee;
"""

    prompt_intro = (
        "You are an expert SQL assistant. Based on the schema and user question, generate only a VALID SQLite SQL query. "
        "Use context from previous turns to understand follow-ups. Do NOT include explanations or formatting.\n\n"
        f"Schema:\n{schema}\n\nSample Rows:\n{sample_rows}\n\nFew-shot Examples:\n{examples}\n\n"
    )

    messages = [{"role": "system", "content": prompt_intro}]
    for turn in history:
        messages.append({"role": "user", "content": turn['question']})
        messages.append({"role": "assistant", "content": turn['answer']})
    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 512,
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"].strip().strip("```sql").strip("```")
    except Exception as e:
        print("Error in generate_sql:", e)
        return "SELECT 'Error';"

@app.post("/query")
def query(input: QueryInput):
    history = get_history(input.session_id)
    sql = generate_sql(input.question, history)

    if not validate_sql(sql):
        return {"error": "Generated SQL is not safe to execute."}

    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        result = f"Database error: {e}"
    finally:
        conn.close()

    answer = generate_natural_answer(input.question, result)
    save_question(input.session_id, input.question, answer)
    updated_history = get_history(input.session_id)

    return {
        "session_id": input.session_id,
        "sql": sql,
        "answer": answer,
        "history": updated_history
    }
