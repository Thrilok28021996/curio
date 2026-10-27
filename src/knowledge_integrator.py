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

        # Check for duplicate content — don't store the same lesson twice
        existing = self.store.search_knowledge()
        lesson_lower = lesson.strip().lower()
        for node in existing:
            if node.content.strip().lower() == lesson_lower:
                # Already have this — just reinforce it
                node.reinforcement_count += 1
                node.last_reinforced = _now()
                self.store.store_knowledge(node)
                self.store.update_gap_status(gap.gap_id, "RESOLVED")
                return node

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
        # Only try LLM if it's actually configured
        try:
            from .llm import get_llm
            llm = get_llm()
            if llm.is_available():
                from .llm import extract_lesson
                lesson = extract_lesson(raw_info.raw_text, gap.topic)
                if lesson and len(lesson) > 10:
                    return lesson
        except Exception as e:
            self.logger.debug(f"LLM extraction failed, using fallback: {e}")

        # Fallback: basic extraction (filters noise)
        return self._simple_extract(gap, raw_info)

    def _simple_extract(self, gap: Gap, raw_info: RawInfo) -> str:
        """Basic extraction without LLM — filters out noise."""
        text = raw_info.raw_text
        topic_words = set(gap.topic.lower().split())
        lines = text.split("\n")

        # Noise patterns to skip
        noise_patterns = [
            "http://", "https://", "www.", ".com", ".org", ".net",
            "cookie", "privacy policy", "terms of service", "sign in",
            "log in", "subscribe", "newsletter", "©", "copyright",
            "see step by step", "click here", "read more", "advertisement",
        ]

        # Date patterns like "Aug 29, 2023 ·"
        import re
        date_pattern = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}')

        relevant_lines = []
        for line in lines:
            line = line.strip()
            if len(line) < 20:
                continue  # Too short to be a lesson
            if len(line) > 500:
                line = line[:500]

            line_lower = line.lower()

            # Skip noise
            if any(noise in line_lower for noise in noise_patterns):
                continue
            if date_pattern.search(line):
                continue

            # Keep if it mentions the topic AND has substance
            if any(word in line_lower for word in topic_words) and len(line) > 30:
                relevant_lines.append(line)

        if relevant_lines:
            # Take the first substantial line
            return relevant_lines[0]

        # Fallback: first meaningful sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and not any(noise in s.lower() for noise in noise_patterns):
                return s[:300]

        return gap.topic  # Last resort: just the topic

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
