import requests

# OLLAMA_URL = "http://localhost:11434/api/generate"

# def ask_llm(prompt):
#     response = requests.post(
#     OLLAMA_URL,
#     json={
#         "model": "qwen3.5:latest",
#         "prompt": prompt,
#         "stream": False,
#         "think": False
#     },
#     timeout=60
# )

#     print("Status:", response.status_code)
#     print("Response:", response.text)

#     response.raise_for_status()

#     return response.json()["response"]

import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def ask_llm(prompt):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text