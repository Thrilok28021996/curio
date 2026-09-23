"""Curio — Web Search Integration.

Lightweight web search using DuckDuckGo (no API keys required).
Falls back gracefully on errors; returns results as simple dicts.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Default result limit
DEFAULT_MAX_RESULTS = 5

# Sleep before each attempt, indexed by attempt number: the first entry is
# 0.0 so the initial attempt is immediate. Retry only the network path —
# a genuine "no results" answer has nothing to back off from.
ATTEMPT_DELAYS = (0.0, 0.5, 1.5)


def web_search(query: str, max_results: int = DEFAULT_MAX_RESULTS) -> list[dict[str, Any]] | None:
    """Search the web via DuckDuckGo and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A list of dicts, each with keys: title, url, snippet.

        An empty list means the backend answered and genuinely found nothing.

        ``None`` means the search could not be performed at all (ddgs not
        installed, or the backend errored on every attempt). Callers must
        not treat ``None`` as "no results exist" — it means "unknown".
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
        return None

    raw_results: list[dict[str, Any]] | None = None
    last_error: Exception | None = None
    attempts = len(ATTEMPT_DELAYS)

    for attempt, delay in enumerate(ATTEMPT_DELAYS, start=1):
        if delay:
            time.sleep(delay)
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query.strip(), max_results=max_results))
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Web search attempt %d/%d failed for %r: %s",
                attempt, attempts, query, exc,
            )
    else:
        # Every attempt raised (the initial one included).
        last_error = last_error or RuntimeError("no attempts were made")

    if last_error is not None or raw_results is None:
        logger.error(
            "Web search failed for query '%s' after %d attempts: %s",
            query, attempts, last_error,
        )
        return None

    results: list[dict[str, Any]] = []
    for item in raw_results:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", ""),
        })

    return results
