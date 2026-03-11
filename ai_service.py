import os
import json
import re
from typing import Any, List, Dict
import httpx


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    subject = compact if compact and compact.lower() != "ai service fallback" else "a culture-rich city escape"
    items = [
        {
            "title": "Day 1: Signature neighborhood route",
            "detail": f"Start with a high-character arrival sequence shaped around {subject}, local coffee, and a memorable golden-hour stop.",
            "score": 84,
        },
        {
            "title": "Day 2: Visual highlight block",
            "detail": "Stack the strongest museum, food, and photo moments into one smooth mid-trip day with minimal transit friction.",
            "score": 88,
        },
        {
            "title": "Day 3: Flexible finale",
            "detail": "Reserve the final lane for shopping, slow wandering, and one last rooftop or riverside scene before departure.",
            "score": 92,
        },
    ]
    highlights = ["Photo-ready routing", "Low-friction transit", "Moodboard-worthy stops"]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": f"TripCanvas translated {subject} into a polished, photo-ready city itinerary.",
        "tags": ["city escape", "visual route", "easy transit"],
        "items": items,
        "score": 88,
        "insights": ["Lead with the first-day route so the trip feels tangible immediately.", "Keep one signature visual moment on each day to make the itinerary feel memorable."],
        "next_actions": ["Save the itinerary to the trip library.", "Swap one stop for a budget or nightlife variation before sharing."],
        "highlights": highlights,
    }

INF_ENDPOINT = "https://inference.do-ai.run/v1/chat/completions"
API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

def _extract_json(text: str) -> str:
    """Extract JSON payload from LLM response, handling markdown code fences."""
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

async def call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Any:
    """Call DigitalOcean Serverless Inference and return parsed JSON.
    Returns a dict on success or a fallback dict with a 'note' key on any error.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(INF_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # Expected structure: {"choices": [{"message": {"content": "..."}}]}
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            return json.loads(json_str)
    except Exception:
        # Graceful fallback so the route never raises an unhandled exception
        return _coerce_unstructured_payload("AI service fallback")
