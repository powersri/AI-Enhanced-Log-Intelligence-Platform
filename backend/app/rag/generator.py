import json
import requests

from app.config import settings


GEMINI_GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def generate_structured_report(prompt: str) -> dict:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")

    response = requests.post(
        f"{GEMINI_GENERATE_URL}?key={settings.GEMINI_API_KEY}",
        json={
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)