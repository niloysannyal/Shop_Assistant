"""
Groq API helper with retries and a robust fallback.

This module tries to call the Groq (OpenAI-compatible) chat completions endpoint.
If the API is unreachable or the response is malformed, a friendly fallback
string is returned so the chatbot can still answer.
"""
import time
import requests
from typing import Optional
from app.core.config import settings

def query_groq(prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_retries: int = 3) -> str:
    model = model or settings.GROQ_MODEL
    url = str(settings.GROQ_API_URL)
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 512
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            # The Groq / OpenAI-compatible response shape:
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or \
                   "Sorry — the AI returned an empty response."
        except Exception as exc:
            # brief exponential-ish backoff
            time.sleep(0.5 * attempt)
            last_exc = exc

    # Final graceful fallback: a short safe reply (not empty) so the higher layer can continue.
    return "Sorry — I couldn't reach the AI service right now. I can still give you a quick product summary if you want."
