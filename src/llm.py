"""Curio — LLM Integration.

Uses an LLM for lesson extraction and source evaluation.
Supports OpenAI-compatible APIs (OpenAI, Anthropic via proxy, local models).

Set CURIO_LLM_API_KEY and CURIO_LLM_BASE_URL environment variables,
or use CURIO_LLM_PROVIDER=openai|anthropic|ollama.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LLMClient:
    """Lightweight LLM client for Curio's learning operations."""

    def __init__(self):
        self.provider = os.environ.get("CURIO_LLM_PROVIDER", "openai")
        self.api_key = os.environ.get("CURIO_LLM_API_KEY", "")
        self.base_url = os.environ.get("CURIO_LLM_BASE_URL", "")
        self.model = os.environ.get("CURIO_LLM_MODEL", "gpt-4o-mini")
        self._client = None

    def _get_client(self):
        """Lazy-init the LLM client."""
        if self._client is not None:
            return self._client

        if self.provider == "ollama":
            base = self.base_url or "http://localhost:11434"
            self._client = ("openai", base, "ollama")
        elif self.provider == "anthropic":
            self._client = ("anthropic", self.api_key, self.model)
        else:
            # OpenAI-compatible (default)
            base = self.base_url or "https://api.openai.com/v1"
            self._client = ("openai", base, self.api_key)

        return self._client

    def chat(self, system: str, user: str, temperature: float = 0.3) -> str:
        """Send a chat completion request and return the response text."""
        client_info = self._get_client()
        provider = client_info[0]

        try:
            if provider == "anthropic":
                return self._call_anthropic(client_info[1], system, user, temperature)
            else:
                return self._call_openai_compatible(client_info[1], client_info[2], system, user, temperature)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ""

    def _call_openai_compatible(
        self, base_url: str, api_key: str,
        system: str, user: str, temperature: float,
    ) -> str:
        """Call an OpenAI-compatible API."""
        import urllib.request

        url = f"{base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": 1000,
        })

        req = urllib.request.Request(
            url, data=payload.encode(), headers=headers, method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]

    def _call_anthropic(
        self, api_key: str,
        system: str, user: str, temperature: float,
    ) -> str:
        """Call the Anthropic API."""
        import urllib.request

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = json.dumps({
            "model": self.model,
            "max_tokens": 1000,
            "temperature": temperature,
            "system": system,
            "messages": [
                {"role": "user", "content": user},
            ],
        })

        req = urllib.request.Request(
            url, data=payload.encode(), headers=headers, method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["content"][0]["text"]

    def is_available(self) -> bool:
        """Check if the LLM client is configured and available."""
        if self.provider == "ollama":
            return True  # Ollama doesn't need an API key
        return bool(self.api_key)


# Singleton
_client: LLMClient | None = None


def get_llm() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


# ============================================================
# Curio-specific LLM operations
# ============================================================

EXTRACT_LESSON_SYSTEM = """You are a lesson extraction engine for an AI learning agent called Curio.

Your job is to distill raw information into a concise, structured lesson that can be stored in a knowledge graph.

Rules:
1. Extract the CORE fact or lesson — not the raw text
2. Be specific and actionable
3. Include version numbers, dates, or technical details when present
4. Keep it under 200 words
5. If the information contradicts something, note the conflict
6. Output as plain text, not markdown

Example input: "FastAPI is a modern Python web framework for building APIs. It uses standard Python type hints. Version 0.115 was released in September 2024 with support for Pydantic v2."

Example output: "FastAPI is a Python web framework for APIs using type hints. Version 0.115 (Sep 2024) supports Pydantic v2."
"""

EVALUATE_SOURCE_SYSTEM = """You are a source quality evaluator for an AI learning agent called Curio.

Given a piece of information and its source URL, evaluate:
1. Reliability: Is this a primary source (official docs), secondary (blog/tutorial), or tertiary (forum/social)?
2. Confidence: How confident should we be in this information? (0.0-1.0)
3. Recency: Does the information seem current or outdated?

Output as JSON:
{"reliability": "PRIMARY|SECONDARY|TERTIARY", "confidence": 0.0-1.0, "recency": "recent|unknown|outdated", "notes": "brief explanation"}
"""


def extract_lesson(raw_text: str, topic: str = "") -> str:
    """Use LLM to extract a concise lesson from raw text.

    Falls back to simple extraction if LLM is unavailable.
    """
    llm = get_llm()

    if not llm.is_available():
        # Fallback: simple extraction
        return _simple_extract(raw_text)

    user_msg = f"Topic: {topic}\n\nRaw information:\n{raw_text[:3000]}"
    result = llm.chat(EXTRACT_LESSON_SYSTEM, user_msg, temperature=0.2)

    if not result or len(result) < 10:
        return _simple_extract(raw_text)

    return result.strip()


def evaluate_source(text: str, url: str = "") -> dict[str, Any]:
    """Use LLM to evaluate source quality.

    Returns dict with reliability, confidence, recency, notes.
    Falls back to defaults if LLM is unavailable.
    """
    llm = get_llm()

    if not llm.is_available():
        return {
            "reliability": "SECONDARY",
            "confidence": 0.5,
            "recency": "unknown",
            "notes": "LLM not available, using default evaluation",
        }

    user_msg = f"Source URL: {url}\n\nInformation:\n{text[:2000]}"
    result = llm.chat(EVALUATE_SOURCE_SYSTEM, user_msg, temperature=0.1)

    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return {
            "reliability": "SECONDARY",
            "confidence": 0.5,
            "recency": "unknown",
            "notes": f"Failed to parse LLM response: {result[:100]}",
        }


def _simple_extract(text: str) -> str:
    """Simple fallback extraction without LLM."""
    # Take first 200 chars, clean up
    lines = text.strip().split("\n")
    relevant = [l.strip() for l in lines if l.strip()][:5]
    return "\n".join(relevant)[:500]
