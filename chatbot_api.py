from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from requests.exceptions import RequestException

app = FastAPI()
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:latest"
OLLAMA_TIMEOUT_SECONDS = 30

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    prompt = (
        "You are a helpful restaurant assistant. "
        "Respond to food and dining-related questions only. "
        "If not related to food, say you can't help.\n"
        f"User: {request.message}\nAssistant:"
    )

    try:
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        ollama_response.raise_for_status()
    except requests.Timeout as exc:
        raise HTTPException(
            status_code=504,
            detail="Timed out contacting Ollama. Make sure Ollama is running.",
        ) from exc
    except RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not contact Ollama: {exc}",
        ) from exc

    try:
        response_data = ollama_response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Ollama returned invalid JSON.") from exc

    reply = response_data.get("response")
    if not isinstance(reply, str) or not reply.strip():
        raise HTTPException(status_code=502, detail="Ollama response was missing text.")

    return {"response": reply}
