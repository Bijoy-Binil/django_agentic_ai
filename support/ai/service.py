import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_llm(prompt):
    response = requests.post(
    OLLAMA_URL,
    json={
        "model": "qwen3.5:latest",
        "prompt": prompt,
        "stream": False,
        "think": False
    },
    timeout=60
)

    print("Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()["response"]