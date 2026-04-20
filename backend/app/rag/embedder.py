import requests

from app.config import settings


GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"


def embed_text(text: str) -> list[float]:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")

    response = requests.post(
        f"{GEMINI_EMBED_URL}?key={settings.GEMINI_API_KEY}",
        json={
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            },
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()
    return data["embedding"]["values"]