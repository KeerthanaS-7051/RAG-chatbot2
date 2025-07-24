import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Employee Chatbot", layout="centered")
st.title("🤖 Employee Database Chatbot")

# Create a session if not already created
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Get user input
question = st.text_input("Ask a question about employees")

if st.button("Submit") and question:
    with st.spinner("Thinking..."):
        response = requests.post("http://localhost:8000/query", json={
            "question": question,
            "session_id": st.session_state.session_id
        })

        try:
            data = response.json()

            # Print the latest answer
            if isinstance(data['answer'], list):
                st.write("Answer:", data['answer'][0][0] if data['answer'] else "No result")
            else:
                st.write("Answer:", data['answer'])

            # Print full history
            st.subheader("Session History")
            for i, entry in enumerate(data['history']):
                q = entry.get('question', 'Unknown question')
                a = entry.get('answer', 'No answer available')
                st.markdown(f"**{i+1}. Question:** {q}")
                st.markdown(f"**Answer:** {a}\n")

        except Exception as e:
            st.error(f"Error: {e}")
            st.text(response.text)
