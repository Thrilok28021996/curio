"""Curio — Knowledge Integrator (Learning Engine).

Processes raw information into durable, structured knowledge.
Validates across sources, compresses to lessons, connects to
existing knowledge, and stores with confidence scoring.
"""

from __future__ import annotations

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
import json
import logging
from .models import (
    AuditAction, Gap, KnowledgeNode, RawInfo, SourceRecord,
    _now, _uuid,
)


class KnowledgeIntegrator:
    """Integrates raw information into stored knowledge."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit
        self.logger = logging.getLogger(__name__)

    def integrate(self, gap: Gap, raw_info: RawInfo) -> KnowledgeNode | None:
        """Process raw information into a knowledge node.

        Steps:
        1. Validate across sources
        2. Extract the core lesson
        3. Connect to existing knowledge
        4. Assign confidence
        5. Store with provenance
        """
        if not raw_info.raw_text.strip():
            return None

        # Validate: check source agreement
        source_count = len(raw_info.sources)
        if source_count == 0:
            confidence = 0.3  # Low confidence, no verified sources
        elif source_count == 1:
            confidence = 0.5
        elif source_count == 2:
            confidence = 0.65
        else:
            confidence = min(0.8, 0.5 + source_count * 0.1)

        # Extract the lesson (compressed, not raw text)
        lesson = self._extract_lesson(gap, raw_info)

        # Find connections to existing knowledge
        connections = self._find_connections(lesson, gap)

        # Store source records
        source_ids = []
        for source in raw_info.sources:
            stored = self.store.store_source(source)
            source_ids.append(stored.source_id)

        # Create the knowledge node
        node = KnowledgeNode(
            content=lesson,
            domain=gap.topic,
            subdomain=gap.type.value,
            confidence=confidence,
            node_type="FACT",
            source_ids=source_ids,
            connections=connections,
            created_at=_now(),
            last_reinforced=_now(),
            last_accessed=_now(),
        )

        # Store it
        self.store.store_knowledge(node)

        # Update gap status
        self.store.update_gap_status(gap.gap_id, "RESOLVED")

        # Update domain map
        self._update_domain_map(gap.topic)

        # Audit
        self.audit.log(
            AuditAction.LEARNED,
            target_id=node.knowledge_id,
            gap_id=gap.gap_id,
            domain=gap.topic,
            confidence=confidence,
            source_count=source_count,
            lesson_preview=lesson[:100],
            connections=len(connections),
        )

        return node

    def _extract_lesson(self, gap: Gap, raw_info: RawInfo) -> str:
        """Extract a concise lesson from raw information.

        Uses LLM for intelligent extraction when available.
        Falls back to basic extraction.
        """
        try:
            from .llm import extract_lesson
            lesson = extract_lesson(raw_info.raw_text, gap.topic)
            if lesson and len(lesson) > 10:
                return lesson
        except Exception as e:
            self.logger.debug(f"LLM extraction failed, using fallback: {e}")

        # Fallback: basic extraction
        return self._simple_extract(gap, raw_info)

    def _simple_extract(self, gap: Gap, raw_info: RawInfo) -> str:
        """Basic extraction without LLM."""
        text = raw_info.raw_text
        topic_lower = gap.topic.lower()
        lines = text.split("\n")

        relevant_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in topic_lower.split()):
                relevant_lines.append(line.strip())
            elif any(marker in line_lower for marker in [
                "is a", "refers to", "means", "defined as",
                "the rule", "the requirement", "must", "shall",
                "config", "setting", "parameter", "default",
            ]):
                relevant_lines.append(line.strip())

        if relevant_lines:
            return "\n".join(relevant_lines[:10])
        return text[:500]

    def _find_connections(self, lesson: str, gap: Gap) -> list[str]:
        """Find existing knowledge nodes that relate to this lesson."""
        connections = []
        lesson_words = set(lesson.lower().split())
        nodes = self.store.search_knowledge()

        for node in nodes:
            if node.knowledge_id in connections:
                continue
            node_words = set(node.content.lower().split())
            overlap = len(lesson_words & node_words)
            if overlap >= 3:  # At least 3 shared words
                connections.append(node.knowledge_id)

        return connections[:10]  # Cap connections

    def _update_domain_map(self, domain: str):
        """Update the domain coverage map after adding knowledge."""
        nodes = self.store.search_knowledge(domain=domain)
        gaps = self.store.get_open_gaps()

        domain_gaps = [g for g in gaps if domain.lower() in g.topic.lower()]

        total_confidence = 0.0
        if nodes:
            total_confidence = sum(n.confidence for n in nodes) / len(nodes)

        self.store.update_domain_map(
            domain=domain,
            knowledge_count=len(nodes),
            active_gaps=len(domain_gaps),
            total_confidence=total_confidence,
        )
