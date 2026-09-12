"""Curio — Main Orchestrator.

Ties all engines together into the autonomous learning loop.
This is the entry point for running Curio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_log import AuditLog
from .gap_detector import GapDetector
from .knowledge_integrator import KnowledgeIntegrator
from .knowledge_map import KnowledgeMap
from .knowledge_seeker import KnowledgeSeeker
from .knowledge_store import KnowledgeStore
from .memory_consolidator import MemoryConsolidator
from .models import (
    AuditAction, ConsolidationReport, Gap, Observation,
    ObservationType, _now,
)
from .relevance_filter import RelevanceFilter


class Curio:
    """The main Curio learning agent.

    Usage:
        curio = Curio()
        curio.observe("The API uses JWT RS256 auth")
        curio.gaps()
        curio.progress()
    """

    def __init__(self, data_dir: str | Path = "~/.curio"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize stores
        self.store = KnowledgeStore(self.data_dir / "knowledge.db")
        self.audit_log = AuditLog(self.data_dir / "audit.jsonl")

        # Initialize engines
        self.detector = GapDetector(self.store, self.audit_log)
        self.filter = RelevanceFilter(self.store, self.audit_log)
        self.seeker = KnowledgeSeeker(self.store, self.audit_log)
        self.integrator = KnowledgeIntegrator(self.store, self.audit_log)
        self.consolidator = MemoryConsolidator(self.store, self.audit_log)
        self.knowledge_map = KnowledgeMap(self.store, self.audit_log)

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def observe(self, content: str, source: str = "",
                obs_type: str = "event", **metadata) -> list[Gap]:
        """Process an observation through the full learning loop.

        This is the main entry point. An observation goes through:
        1. Perceive (normalize)
        2. Detect gaps
        3. Appraise each gap
        4. Learn if worth it
        """
        # Create observation
        obs = Observation(
            type=ObservationType(obs_type),
            content=content,
            source=source,
            metadata=metadata,
        )

        self.audit_log.log(AuditAction.OBSERVE, content=content[:200], source=source)

        # Detect gaps
        gaps = self.detector.detect(obs)

        # Appraise and learn
        for gap in gaps:
            appraisal = self.filter.appraise(gap)

            if appraisal.decision.value == "LEARN":
                # Seek information
                raw_info = self.seeker.seek(gap, appraisal.suggested_sources)

                if raw_info:
                    # Integrate into knowledge
                    node = self.integrator.integrate(gap, raw_info)
                    if node:
                        self.audit_log.log(
                            AuditAction.STORED,
                            target_id=node.knowledge_id,
                            gap_id=gap.gap_id,
                        )
                    else:
                        # Integration failed — keep gap open
                        pass
                else:
                    # No info found — keep gap open
                    pass

            elif appraisal.decision.value == "DEFER":
                self.store.update_gap_status(gap.gap_id, "DEFERRED")

            else:  # IGNORE
                self.store.update_gap_status(gap.gap_id, "IGNORED")

        return gaps

    def teach(self, content: str, domain: str = "", confidence: float = 0.8) -> Any:
        """Directly teach Curio something.

        This bypasses the learning loop and stores a knowledge
        node directly. Use this for facts you want Curio to know.
        """
        from .models import KnowledgeNode, _now

        if not domain:
            # Extract domain from first few words
            domain = " ".join(content.split()[:6])

        node = KnowledgeNode(
            content=content,
            domain=domain,
            confidence=confidence,
            node_type="FACT",
            created_at=_now(),
            last_reinforced=_now(),
            last_accessed=_now(),
        )

        self.store.store_knowledge(node)
        self.audit_log.log(
            AuditAction.STORED,
            target_id=node.knowledge_id,
            source="direct_teach",
            domain=domain,
        )

        return node

    def gaps(self, priority: str = "") -> list[dict[str, Any]]:
        """Show open knowledge gaps."""
        return self.knowledge_map.what_i_dont_know()

    def know(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Show what Curio knows, ranked by confidence."""
        return self.knowledge_map.what_i_know(top_n)

    def progress(self) -> dict[str, Any]:
        """Show learning progress and coverage."""
        return self.knowledge_map.coverage_report()

    def confidence(self, topic: str) -> float:
        """Check Curio's confidence about a specific topic."""
        return self.knowledge_map.confidence(topic)

    def consolidate(self) -> ConsolidationReport:
        """Run a consolidation cycle (decay, compress, prune)."""
        return self.consolidator.consolidate()

    def show_audit(self, last_n: int = 20) -> list[dict[str, Any]]:
        """Show recent audit log entries."""
        return self.audit_log.read(last_n)

    def stats(self) -> dict[str, Any]:
        """Show store statistics."""
        return self.store.stats()

    def close(self):
        """Clean up resources."""
        self.store.close()

    # ----------------------------------------------------------
    # Context manager
    # ----------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
