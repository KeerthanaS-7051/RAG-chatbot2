from fastapi import FastAPI
from pydantic import BaseModel
from mcp_servers.sql_generator import generate_sql
from api_service import query_employee_db
from session_store import save_question, get_history
import os
import requests
import sqlparse

app = FastAPI()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def generate_natural_answer(question: str, answer) -> str:
    if isinstance(answer, list):
        answer = str(answer)

    prompt = (
        "You are a helpful assistant that answers questions based on employee database results.\n\n"
        f"User question: {question}\n"
        f"Answer from database: {answer}\n\n"
        "Provide a natural, concise, human-readable answer."
    )

    payload = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": "Be brief, clear, and helpful."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150,
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Error generating natural answer:", e)
        return f"The answer is: {answer}"

def is_valid_sql(sql: str) -> bool:
    try:
        parsed = sqlparse.parse(sql)          
        if not parsed:
            return False                    

        stmt = parsed[0]                     
        return stmt.get_type() == 'SELECT' 
    except Exception as e:
        print("SQL validation error:", e)
        return False

class QueryInput(BaseModel):
    question: str
    session_id: str

@app.post("/query")
def query(input: QueryInput):
    history = get_history(input.session_id)

    sql = generate_sql(input.question, history=history)

    if not is_valid_sql(sql):
        natural_answer = "I generated an invalid or unsafe SQL query. Please rephrase your question."
        save_question(input.session_id, input.question, natural_answer)
        return {
            "session_id": input.session_id,
            "sql": sql,
            "answer": natural_answer,
            "history": get_history(input.session_id)
        }

    raw_answer = query_employee_db(sql)
    natural_answer = generate_natural_answer(input.question, raw_answer)

    save_question(input.session_id, input.question, natural_answer)

    return {
        "session_id": input.session_id,
        "sql": sql,
        "answer": natural_answer,
        "history": get_history(input.session_id)
    }
