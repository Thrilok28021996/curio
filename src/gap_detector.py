"""Curio — Gap Detector (Curiosity Engine).

Detects knowledge gaps from observations by comparing against
stored knowledge. This is the "curiosity signal" — the system
saying "I don't know this" or "I was wrong about this."
"""

from __future__ import annotations

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
from .models import (
    AuditAction, Gap, GapType, Observation, Priority, _now,
)


class GapDetector:
    """Detects knowledge gaps from incoming observations."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit

    def detect(self, observation: Observation) -> list[Gap]:
        """Analyze an observation and return detected gaps.

        For each observation, the detector:
        1. Searches existing knowledge for related content
        2. Classifies the gap type based on what's found (or not found)
        3. Assigns priority based on gap type and frequency
        """
        gaps: list[Gap] = []

        # Search for related knowledge
        related = self.store.search_knowledge()
        matches = self._find_related(observation.content, related)

        if not matches:
            # No related knowledge at all → UNKNOWN gap
            gap = Gap(
                type=GapType.UNKNOWN,
                topic=self._extract_topic(observation.content),
                description=f"No knowledge found about: {observation.content[:200]}",
                confidence=0.3,
                priority=self._estimate_priority(observation),
                source_observation=observation.observation_id,
            )
            gaps.append(gap)

        else:
            # Check for partial matches → INCOMPLETE
            best_match = matches[0]
            similarity = best_match["similarity"]

            if similarity < 0.4:
                # Weak match — knowledge exists but doesn't cover this well
                gap = Gap(
                    type=GapType.INCOMPLETE,
                    topic=self._extract_topic(observation.content),
                    description=(
                        f"Partial knowledge exists (similarity={similarity:.2f}) "
                        f"but may not cover: {observation.content[:200]}"
                    ),
                    confidence=0.5,
                    priority=self._estimate_priority(observation),
                    source_observation=observation.observation_id,
                )
                gaps.append(gap)

            elif similarity < 0.7:
                # Moderate match — check for staleness
                node = best_match["node"]
                days_old = self._days_since(node.last_reinforced)
                if days_old > 30:
                    gap = Gap(
                        type=GapType.OUTDATED,
                        topic=node.domain or self._extract_topic(observation.content),
                        description=(
                            f"Knowledge may be outdated "
                            f"(last reinforced {days_old} days ago). "
                            f"Observation: {observation.content[:200]}"
                        ),
                        confidence=0.6,
                        priority=self._estimate_priority(observation),
                        source_observation=observation.observation_id,
                    )
                    gaps.append(gap)

            # Check for contradictions with the observation content
            contradiction = self._check_contradiction(observation, matches)
            if contradiction:
                gaps.append(contradiction)

        # Store detected gaps
        for gap in gaps:
            self.store.store_gap(gap)
            self.audit.log(
                AuditAction.GAP_DETECTED,
                target_id=gap.gap_id,
                gap_type=gap.type.value,
                topic=gap.topic,
                priority=gap.priority.value,
                confidence=gap.confidence,
            )

        return gaps

    def _find_related(
        self, content: str, nodes: list, threshold: float = 0.2
    ) -> list[dict]:
        """Find knowledge nodes related to the content.

        Uses keyword overlap as a lightweight similarity measure.
        In production, this would use embedding cosine similarity.
        """
        content_words = set(content.lower().split())
        matches = []

        for node in nodes:
            node_words = set(node.content.lower().split())
            if not node_words:
                continue
            overlap = len(content_words & node_words)
            similarity = overlap / max(len(content_words), len(node_words))
            if similarity >= threshold:
                matches.append({"node": node, "similarity": similarity})

        matches.sort(key=lambda m: m["similarity"], reverse=True)
        return matches

    def _extract_topic(self, content: str) -> str:
        """Extract a short topic label from content.

        Uses the first meaningful words as a topic label.
        """
        words = content.split()[:8]
        return " ".join(words) if words else "unknown"

    def _estimate_priority(self, observation: Observation) -> Priority:
        """Estimate gap priority based on observation context."""
        # Errors and system events are high priority
        if observation.type.value in ("error", "system"):
            return Priority.HIGH

        # Check metadata for explicit priority signals
        if observation.metadata.get("priority") == "HIGH":
            return Priority.HIGH

        # Default to medium
        return Priority.MEDIUM

    def _check_contradiction(
        self, observation: Observation, matches: list[dict]
    ) -> Gap | None:
        """Check if the observation contradicts stored knowledge.

        Checks for:
        1. Negation patterns (is not, doesn't, etc.)
        2. Replacement signals (now uses, replaced with, etc.)
        3. Value conflicts (different values for same key)
        4. Explicit deprecation markers
        """
        content_lower = observation.content.lower()

        # Contradiction signals
        negation_patterns = [
            "is not", "doesn't", "does not", "is no longer",
            "was changed to", "was updated to", "now uses",
            "replaced with", "deprecated", "removed",
            "switched to", "migrated to", "upgraded to",
            "downgraded to", "was replaced", "no longer uses",
        ]

        for match in matches:
            node = match["node"]
            node_lower = node.content.lower()

            # Check negation patterns
            for pattern in negation_patterns:
                if pattern in content_lower:
                    # Check if the stored knowledge has a conflicting value
                    # Extract key terms from both
                    node_terms = set(node_lower.split()) - {"the", "a", "an", "is", "are", "was", "were", "for", "with", "and", "or"}
                    content_terms = set(content_lower.split()) - {"the", "a", "an", "is", "are", "was", "were", "for", "with", "and", "or"}

                    # If both mention similar topics but different values
                    common = node_terms & content_terms
                    if len(common) >= 2:
                        return Gap(
                            type=GapType.CONTRADICTORY,
                            topic=node.domain or self._extract_topic(observation.content),
                            description=(
                                f"Observation contradicts stored knowledge. "
                                f"Stored: {node.content[:150]}... "
                                f"New: {observation.content[:150]}..."
                            ),
                            confidence=0.5,
                            priority=Priority.HIGH,
                            source_observation=observation.observation_id,
                        )

            # Check for value conflicts on technical terms
            # Look for patterns like "X uses Y" vs "X uses Z"
            import re
            uses_pattern = r"(?:uses?|uses?|configured? as|set to|default[sd]? to)\s+(\S+)"
            node_uses = re.findall(uses_pattern, node_lower)
            content_uses = re.findall(uses_pattern, content_lower)

            if node_uses and content_uses:
                # Both specify a value — check if they conflict
                for nv in node_uses:
                    for cv in content_uses:
                        if (nv != cv and len(nv) > 2 and len(cv) > 2
                                and nv not in ("a", "an", "the")
                                and cv not in ("a", "an", "the")):
                            # Different values — likely contradiction
                            return Gap(
                                type=GapType.CONTRADICTORY,
                                topic=node.domain or self._extract_topic(observation.content),
                                description=(
                                    f"Value conflict detected. "
                                    f"Stored: {nv} | New: {cv}. "
                                    f"Stored: {node.content[:100]}... "
                                    f"New: {observation.content[:100]}..."
                                ),
                                confidence=0.6,
                                priority=Priority.HIGH,
                                source_observation=observation.observation_id,
                            )

        return None

    def _days_since(self, date_str: str) -> int:
        """Calculate days since a date string."""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            now = datetime.utcnow()
            return (now - dt.replace(tzinfo=None)).days
        except (ValueError, TypeError):
            return 0
