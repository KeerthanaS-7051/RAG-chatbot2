import uuid

session_data={}

def create_session_id():
    return str(uuid.uuid4())

def save_question(session_id, question, answer):
    if session_id not in session_data:
        session_data[session_id] = []
    session_data[session_id].append({"question": question, "answer": answer})

def get_history(session_id: str):
    return session_data.get(session_id, [])
