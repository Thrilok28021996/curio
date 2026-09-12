"""Curio — Knowledge Map (Metacognition Engine).

Gives Curio self-awareness of what it knows, what it's unsure
about, and what it doesn't know. The "meta" layer.
"""

from __future__ import annotations

from typing import Any

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
from .models import DomainStatus


class KnowledgeMap:
    """Tracks domain coverage and confidence — Curio's self-awareness."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit

    def status(self, domain: str = "") -> DomainStatus | list[DomainStatus]:
        """Get knowledge status for a domain or all domains."""
        if domain:
            return self._domain_status(domain)
        return self._all_domains()

    def what_i_know(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Return the top N things Curio knows, by confidence."""
        nodes = self.store.search_knowledge()
        nodes.sort(key=lambda n: n.confidence, reverse=True)

        return [
            {
                "id": n.knowledge_id,
                "content": n.content[:120],
                "domain": n.domain,
                "confidence": round(n.confidence, 3),
                "sources": len(n.source_ids),
                "access_count": n.access_count,
                "last_accessed": n.last_accessed,
            }
            for n in nodes[:top_n]
        ]

    def what_i_dont_know(self) -> list[dict[str, Any]]:
        """Return all open knowledge gaps, prioritized."""
        gaps = self.store.get_open_gaps()

        return [
            {
                "id": g.gap_id,
                "type": g.type.value,
                "topic": g.topic,
                "priority": g.priority.value,
                "confidence": round(g.confidence, 3),
                "created": g.created_at,
            }
            for g in gaps
        ]

    def coverage_report(self) -> dict[str, Any]:
        """Generate a full coverage report."""
        stats = self.store.stats()
        domains = self._all_domains()
        gaps = self.what_i_dont_know()

        high_priority = sum(1 for g in gaps if g["priority"] == "HIGH")
        medium_priority = sum(1 for g in gaps if g["priority"] == "MEDIUM")
        low_priority = sum(1 for g in gaps if g["priority"] == "LOW")

        return {
            "summary": stats,
            "domains": [
                {
                    "domain": d.domain,
                    "confidence": round(d.total_confidence, 3),
                    "coverage": d.coverage,
                    "knowledge_count": d.knowledge_count,
                    "active_gaps": d.active_gaps,
                }
                for d in domains
            ],
            "gaps": {
                "total": len(gaps),
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority,
            },
        }

    def confidence(self, topic: str) -> float:
        """Return Curio's confidence about a specific topic."""
        nodes = self.store.search_knowledge()
        topic_lower = topic.lower()

        relevant = [
            n for n in nodes
            if topic_lower in n.domain.lower()
            or topic_lower in n.content.lower()
        ]

        if not relevant:
            return 0.0

        # Weighted average: higher confidence nodes count more
        total_weight = sum(n.confidence for n in relevant)
        weighted_sum = sum(n.confidence * n.confidence for n in relevant)
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _domain_status(self, domain: str) -> DomainStatus:
        """Get status for a single domain."""
        nodes = self.store.search_knowledge(domain=domain)
        gaps = self.store.get_open_gaps()

        domain_gaps = [g for g in gaps if domain.lower() in g.topic.lower()]

        total_confidence = 0.0
        if nodes:
            total_confidence = sum(n.confidence for n in nodes) / len(nodes)

        coverage = "NONE"
        if total_confidence > 0.8 and len(domain_gaps) == 0:
            coverage = "HIGH"
        elif total_confidence > 0.5:
            coverage = "MEDIUM"
        elif total_confidence > 0:
            coverage = "LOW"

        return DomainStatus(
            domain=domain,
            total_confidence=total_confidence,
            coverage=coverage,
            active_gaps=len(domain_gaps),
            knowledge_count=len(nodes),
            last_updated=nodes[0].last_reinforced if nodes else "",
        )

    def _all_domains(self) -> list[DomainStatus]:
        """Get status for all tracked domains."""
        domains = self.store.get_domain_map()
        result = []

        for d in domains:
            result.append(DomainStatus(
                domain=d["domain"],
                total_confidence=d["total_confidence"],
                coverage=d["coverage"],
                active_gaps=d["active_gaps"],
                knowledge_count=d["knowledge_count"],
                last_updated=d["last_updated"],
            ))

        return result
