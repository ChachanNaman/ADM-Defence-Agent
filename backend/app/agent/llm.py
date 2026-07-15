"""Thin wrapper around the OpenAI SDK pointed at OpenRouter or Groq (PRD section 5).

Which provider is live is decided entirely in app/config.py via LLM_PROVIDER —
this module only ever sees LLM_API_KEY / LLM_BASE_URL / LLM_MODEL, so it does
not need to know or care which one is active.
"""

import json
import re
import time

import openai
from openai import OpenAI

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER

_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

# Free-tier LLM APIs fail in two distinct shapes, both observed in practice
# against OpenRouter, and they need different handling:
#   1. HTTP 200 with an empty `choices` + an `error` field under worker-pool
#      load ("Worker local total request limit reached") — transient, worth
#      retrying with backoff.
#   2. An actual HTTP 429 (`openai.RateLimitError`) for a *daily* cap
#      ("free-models-per-day") — this is scoped to the calendar day, so
#      retrying within the same request does nothing but burn time; it must
#      fail fast instead. Per-minute/per-token 429s (what Groq's free tier
#      returns) are transient and worth the normal backoff.
_MAX_RETRIES = 5
_BACKOFF_SECONDS = 2.0


def complete_text(system: str, user: str, temperature: float = 0.3) -> str:
    last_error = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = _client.chat.completions.create(
                model=LLM_MODEL,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except openai.RateLimitError as exc:
            message = str(exc)
            if "per-day" in message or "per day" in message or "daily" in message.lower():
                raise RuntimeError(f"{LLM_PROVIDER} daily free-tier quota exhausted: {exc}") from exc
            last_error = exc
            time.sleep(_BACKOFF_SECONDS * (2**attempt))
            continue
        except openai.APIStatusError as exc:
            last_error = exc
            time.sleep(_BACKOFF_SECONDS * (2**attempt))
            continue

        if response.choices:
            return (response.choices[0].message.content or "").strip()
        last_error = getattr(response, "error", None)
        time.sleep(_BACKOFF_SECONDS * (2**attempt))
    raise RuntimeError(f"{LLM_PROVIDER} call failed after {_MAX_RETRIES} retries: {last_error}")


def complete_json(system: str, user: str, temperature: float = 0.1) -> dict:
    """Calls the model and parses a JSON object from its reply.

    The model is untrusted at this boundary (free-tier model, no guaranteed
    structured-output mode) so parsing failure is a real, expected case —
    callers get an explicit `_parse_error` key instead of a raised exception,
    and the caller decides the safe fallback (this agent's is ESCALATE).
    """
    try:
        raw = complete_text(system, user, temperature=temperature)
    except RuntimeError as exc:
        return {"_parse_error": True, "_raw": str(exc)}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = _JSON_BLOCK_RE.search(raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"_parse_error": True, "_raw": raw}
