"""Curio — Knowledge Seeker (Exploration Engine).

Finds and retrieves information to fill validated gaps.
This is the "active exploration" step — like a child
asking questions, reading books, or experimenting.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
from .models import (
    AuditAction, Gap, RawInfo, SourceRecord, _now, _uuid,
)


class KnowledgeSeeker:
    """Searches for and retrieves information to fill knowledge gaps."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit
        self.max_sources = 5
        self.max_chars_per_source = 10_000
        self.agreement_threshold = 3  # stop early if N sources agree

    def seek(self, gap: Gap, suggested_sources: list[str] | None = None) -> RawInfo | None:
        """Seek information to fill a gap.

        Steps:
        1. Identify source candidates
        2. Retrieve content from candidates
        3. Record provenance
        4. Return raw information package

        Returns None if no information was found.
        """
        # Build search queries from the gap
        queries = self._build_queries(gap)

        # Retrieve from local knowledge first
        local_results = self._search_local(gap)

        # In production, this would also search the web
        # For now, we collect what we can find locally
        sources: list[SourceRecord] = []
        raw_texts: list[str] = []

        # Add local results
        for result in local_results:
            source = SourceRecord(
                url=result.get("path", ""),
                title=result.get("title", ""),
                trust_score=result.get("trust", 0.8),
                reliability="PRIMARY" if result.get("is_primary") else "SECONDARY",
            )
            sources.append(source)
            raw_texts.append(result.get("content", ""))

        # If we found enough, package it
        if not raw_texts:
            self.audit.log(
                AuditAction.SEEK,
                target_id=gap.gap_id,
                result="NO_SOURCES_FOUND",
                queries=queries,
            )
            return None

        # Combine raw texts (respecting char limit)
        combined = "\n\n".join(raw_texts)
        if len(combined) > self.max_chars_per_source:
            combined = combined[:self.max_chars_per_source]

        raw_info = RawInfo(
            gap_id=gap.gap_id,
            raw_text=combined,
            sources=sources,
        )

        # Audit
        self.audit.log(
            AuditAction.SEEK,
            target_id=gap.gap_id,
            sources_found=len(sources),
            total_chars=len(combined),
            queries=queries,
        )

        return raw_info

    def _build_queries(self, gap: Gap) -> list[str]:
        """Build search queries from a gap."""
        queries = []

        # Primary query: the topic itself
        queries.append(gap.topic)

        # Secondary query: topic + context
        if gap.type.value == "OUTDATED":
            queries.append(f"{gap.topic} latest update changelog")
        elif gap.type.value == "CONTRADICTORY":
            queries.append(f"{gap.topic} correct current")
        elif gap.type.value == "UNKNOWN":
            queries.append(f"{gap.topic} documentation guide")
        elif gap.type.value == "INCOMPLETE":
            queries.append(f"{gap.topic} details explained")

        return queries

    def _search_local(self, gap: Gap) -> list[dict[str, Any]]:
        """Search local knowledge store for related information."""
        results = []
        nodes = self.store.search_knowledge()

        topic_words = set(gap.topic.lower().split())

        for node in nodes:
            node_words = set(node.content.lower().split())
            overlap = len(topic_words & node_words)
            if overlap > 0:
                similarity = overlap / max(len(topic_words), len(node_words))
                results.append({
                    "path": f"knowledge://{node.knowledge_id}",
                    "title": node.content[:80],
                    "content": node.content,
                    "trust": node.confidence,
                    "is_primary": node.node_type == "FACT",
                    "similarity": similarity,
                })

        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:self.max_sources]

    def record_source_accuracy(self, source_id: str, was_accurate: bool):
        """Record whether a source was accurate when used.

        This builds the trust score over time.
        """
        source = self.store.get_source(source_id)
        if not source:
            return

        source.accuracy_history.append(1.0 if was_accurate else 0.0)
        source.access_count += 1

        # Update trust score as rolling average of accuracy
        if source.accuracy_history:
            source.trust_score = sum(source.accuracy_history) / len(
                source.accuracy_history
            )

        source.last_verified = _now()
        self.store.store_source(source)
