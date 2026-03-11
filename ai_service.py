import os
import json
import re
from typing import Any, List, Dict
import httpx


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
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
        return {"note": "AI service is temporarily unavailable. Please try again later."}
