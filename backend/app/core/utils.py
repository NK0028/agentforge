"""AgentForge Core Utility Functions"""
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def get_timestamp() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def extract_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extracts and parses JSON from LLM output.
    Handles:
    - Pure JSON strings
    - Markdown fenced blocks (```json ... ``` or ``` ...)
    - JSON embedded inside conversational text
    - Trailing commas and basic formatting artifacts
    """
    if not text or not isinstance(text, str):
        return None

    cleaned = text.strip()

    # 1. Direct parse attempt
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Extract from markdown code fences: ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(fence_pattern, cleaned, re.IGNORECASE)
    for match in matches:
        try:
            return json.loads(match.strip())
        except Exception:
            continue

    # 3. Find outermost matching curly braces { ... }
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidate = cleaned[start_idx:end_idx + 1]
        try:
            return json.loads(candidate)
        except Exception:
            # Try removing trailing commas before closing braces/brackets
            sanitized = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(sanitized)
            except Exception:
                pass

    return None
