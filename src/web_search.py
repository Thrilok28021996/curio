"""Curio — Web Search Integration.

Lightweight web search using DuckDuckGo (no API keys required).
Falls back gracefully on errors; returns results as simple dicts.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Default result limit
DEFAULT_MAX_RESULTS = 5


def web_search(query: str, max_results: int = DEFAULT_MAX_RESULTS) -> list[dict[str, Any]]:
    """Search the web via DuckDuckGo and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A list of dicts, each with keys: title, url, snippet.
        Returns an empty list on error or if no results found.
    """
    if not query or not query.strip():
        logger.warning("Empty search query; returning no results.")
        return []

    try:
        from ddgs import DDGS  # noqa: E402
    except ImportError:
        logger.error(
            "ddgs package not installed. Run: pip install ddgs"
        )
        return []

    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query.strip(), max_results=max_results))
    except Exception as exc:
        logger.error("Web search failed for query '%s': %s", query, exc)
        return []

    results: list[dict[str, Any]] = []
    for item in raw_results:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", ""),
        })

    return results
