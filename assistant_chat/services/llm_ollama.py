import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b" 

def generate(prompt: str) -> str:
    payload = {
    "model": OLLAMA_MODEL,
    "prompt": prompt,
    "stream": False,
    "format": "json",
    "options": {
        "temperature": 0.3,
        "top_p": 0.9,
        "num_ctx": 2048
    }
}
    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    return data.get("response", "").strip()