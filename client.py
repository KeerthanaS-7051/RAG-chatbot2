import requests

question = input("Ask about employees: ")
response = requests.post("http://localhost:8000/query", json={"question": question})
print(response.json())
