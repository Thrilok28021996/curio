"""Curio — Memory Consolidator (Forgetting Engine).

Maintains knowledge quality through selective forgetting
and compression. Like sleep consolidation in children —
periodically review, strengthen, compress, and prune.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
from .models import (
    AuditAction, ConsolidationReport, KnowledgeNode, _now,
)


class MemoryConsolidator:
    """Consolidates memory through decay, compression, and pruning."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit
        self.decay_rate = 0.995
        self.prune_threshold = 0.1
        self.archive_threshold = 0.2
        self.archive_age_days = 90
        self.compression_overlap_threshold = 0.8

    def consolidate(self) -> ConsolidationReport:
        """Run a full consolidation cycle.

        Steps:
        1. Decay unused knowledge
        2. Compress similar nodes
        3. Prune low-confidence knowledge
        4. Reinforce frequently-used knowledge
        """
        report = ConsolidationReport()

        nodes = self.store.search_knowledge(include_archived=True)
        active_nodes = [n for n in nodes if not n.is_archived and not n.is_deleted]

        report.total_nodes = len(active_nodes)

        # Step 1: Decay
        decayed = self._decay(active_nodes)
        report.nodes_decayed = decayed

        # Step 2: Compress (merge similar)
        compressed = self._compress(active_nodes)
        report.nodes_compressed = compressed

        # Step 3: Prune (archive or delete)
        pruned = self._prune(active_nodes)
        report.nodes_pruned = pruned

        # Step 4: Reinforce frequently used
        reinforced = self._reinforce(active_nodes)
        report.nodes_reinforced = reinforced

        # Calculate average confidence
        remaining = self.store.search_knowledge()
        if remaining:
            report.avg_confidence = sum(
                n.confidence for n in remaining
            ) / len(remaining)

        # Audit
        self.audit.log(
            AuditAction.CONSOLIDATED,
            nodes_decayed=decayed,
            nodes_compressed=compressed,
            nodes_pruned=pruned,
            nodes_reinforced=reinforced,
            total_nodes=report.total_nodes,
            avg_confidence=report.avg_confidence,
        )

        return report

    def _decay(self, nodes: list[KnowledgeNode]) -> int:
        """Reduce confidence of unused knowledge."""
        count = 0
        now = datetime.utcnow()

        for node in nodes:
            days_since_access = self._days_since(node.last_accessed)
            if days_since_access <= 0:
                continue

            # Don't decay if recently reinforced
            days_since_reinforce = self._days_since(node.last_reinforced)
            if days_since_reinforce < 7:
                continue

            old_confidence = node.confidence
            new_confidence = node.confidence * (
                self.decay_rate ** days_since_access
            )

            # Don't decay below 0.05
            new_confidence = max(0.05, new_confidence)

            if new_confidence != old_confidence:
                node.confidence = new_confidence
                self.store.store_knowledge(node)
                count += 1

                self.audit.log(
                    AuditAction.DECAYED,
                    target_id=node.knowledge_id,
                    old_confidence=round(old_confidence, 3),
                    new_confidence=round(new_confidence, 3),
                    days_since_access=days_since_access,
                )

        return count

    def _compress(self, nodes: list[KnowledgeNode]) -> int:
        """Merge similar knowledge nodes."""
        count = 0
        merged_ids: set[str] = set()

        for i, node_a in enumerate(nodes):
            if node_a.knowledge_id in merged_ids:
                continue

            for node_b in nodes[i + 1:]:
                if node_b.knowledge_id in merged_ids:
                    continue

                overlap = self._calculate_overlap(node_a.content, node_b.content)
                if overlap >= self.compression_overlap_threshold:
                    # Merge: keep the higher-confidence version
                    if node_a.confidence >= node_b.confidence:
                        winner, loser = node_a, node_b
                    else:
                        winner, loser = node_b, node_a

                    # Transfer connections from loser to winner
                    for conn in loser.connections:
                        if conn not in winner.connections:
                            winner.connections.append(conn)

                    # Boost winner's confidence slightly from the merge
                    winner.confidence = min(1.0, winner.confidence + 0.05)
                    winner.reinforcement_count += 1
                    winner.last_reinforced = _now()

                    self.store.store_knowledge(winner)

                    # Archive the loser
                    loser.is_archived = True
                    self.store.store_knowledge(loser)
                    merged_ids.add(loser.knowledge_id)
                    count += 1

                    self.audit.log(
                        AuditAction.UPDATED,
                        target_id=winner.knowledge_id,
                        action="MERGE",
                        merged_from=loser.knowledge_id,
                        overlap=overlap,
                    )

        return count

    def _prune(self, nodes: list[KnowledgeNode]) -> int:
        """Archive or delete low-confidence knowledge."""
        count = 0
        now = datetime.utcnow()

        for node in nodes:
            if node.is_archived or node.is_deleted:
                continue

            days_since_access = self._days_since(node.last_accessed)

            # Hard delete: very low confidence
            if node.confidence < self.prune_threshold:
                node.is_deleted = True
                self.store.store_knowledge(node)
                count += 1

                self.audit.log(
                    AuditAction.PRUNED,
                    target_id=node.knowledge_id,
                    confidence=node.confidence,
                    days_since_access=days_since_access,
                    prune_action="DELETE",
                )

            # Archive: low confidence + old
            elif (node.confidence < self.archive_threshold
                  and days_since_access > self.archive_age_days):
                node.is_archived = True
                self.store.store_knowledge(node)
                count += 1

                self.audit.log(
                    AuditAction.ARCHIVED,
                    target_id=node.knowledge_id,
                    confidence=node.confidence,
                    days_since_access=days_since_access,
                )

        return count

    def _reinforce(self, nodes: list[KnowledgeNode]) -> int:
        """Strengthen frequently-used knowledge."""
        count = 0

        for node in nodes:
            if node.is_archived or node.is_deleted:
                continue

            # Reinforce based on access count
            if node.access_count >= 5 and node.confidence < 0.95:
                old = node.confidence
                node.confidence = min(1.0, node.confidence + 0.05)
                node.reinforcement_count += 1
                node.last_reinforced = _now()
                self.store.store_knowledge(node)
                count += 1

                self.audit.log(
                    AuditAction.REINFORCED,
                    target_id=node.knowledge_id,
                    old_confidence=round(old, 3),
                    new_confidence=round(node.confidence, 3),
                    access_count=node.access_count,
                )

        return count

    def _calculate_overlap(self, text_a: str, text_b: str) -> float:
        """Calculate word-level overlap between two texts."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        return intersection / union if union > 0 else 0.0

    def _days_since(self, date_str: str) -> int:
        """Calculate days since a date string."""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            now = datetime.utcnow()
            return (now - dt.replace(tzinfo=None)).days
        except (ValueError, TypeError):
            return 0
