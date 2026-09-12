"""Curio — Core data models.

All types used across the learning loop.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ============================================================
# Enums
# ============================================================

class ObservationType(str, Enum):
    QUERY = "query"
    EVENT = "event"
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    ERROR = "error"
    SYSTEM = "system"


class GapType(str, Enum):
    UNKNOWN = "UNKNOWN"
    INCOMPLETE = "INCOMPLETE"
    OUTDATED = "OUTDATED"
    CONTRADICTORY = "CONTRADICTORY"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LearningDecision(str, Enum):
    LEARN = "LEARN"
    DEFER = "DEFER"
    IGNORE = "IGNORE"


class AuditAction(str, Enum):
    OBSERVE = "OBSERVE"
    COMPARE = "COMPARE"
    GAP_DETECTED = "GAP_DETECTED"
    APPRAISED = "APPRAISED"
    SEEK = "SEEK"
    LEARNED = "LEARNED"
    STORED = "STORED"
    UPDATED = "UPDATED"
    CONSOLIDATED = "CONSOLIDATED"
    DECAYED = "DECAYED"
    PRUNED = "PRUNED"
    ARCHIVED = "ARCHIVED"
    REINFORCED = "REINFORCED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


# ============================================================
# Core records
# ============================================================

def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Observation:
    """A raw input event that Curio perceives."""
    observation_id: str = field(default_factory=_uuid)
    type: ObservationType = ObservationType.EVENT
    content: str = ""
    source: str = ""
    timestamp: str = field(default_factory=_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Gap:
    """A detected knowledge gap."""
    gap_id: str = field(default_factory=_uuid)
    type: GapType = GapType.UNKNOWN
    topic: str = ""
    description: str = ""
    confidence: float = 0.5
    priority: Priority = Priority.MEDIUM
    source_observation: str = ""
    created_at: str = field(default_factory=_now)
    status: str = "OPEN"  # OPEN | LEARNING | RESOLVED | DEFERRED | IGNORED


@dataclass
class Appraisal:
    """The result of appraising a gap."""
    gap_id: str = ""
    decision: LearningDecision = LearningDecision.IGNORE
    relevance_score: float = 0.0
    reasoning: str = ""
    suggested_sources: list[str] = field(default_factory=list)


@dataclass
class SourceRecord:
    """A verified information source."""
    source_id: str = field(default_factory=_uuid)
    url: str = ""
    title: str = ""
    trust_score: float = 0.5
    reliability: str = "SECONDARY"  # PRIMARY | SECONDARY | TERTIARY
    last_verified: str = field(default_factory=_now)
    access_count: int = 0
    accuracy_history: list[float] = field(default_factory=list)


@dataclass
class RawInfo:
    """Raw information retrieved to fill a gap."""
    info_id: str = field(default_factory=_uuid)
    gap_id: str = ""
    raw_text: str = ""
    sources: list[SourceRecord] = field(default_factory=list)
    retrieved_at: str = field(default_factory=_now)


@dataclass
class KnowledgeNode:
    """A stored lesson — the core unit of Curio's memory."""
    knowledge_id: str = field(default_factory=_uuid)
    content: str = ""  # The lesson, not raw text
    domain: str = ""
    subdomain: str = ""
    confidence: float = 0.5
    node_type: str = "FACT"  # FACT | PROCEDURE | PREFERENCE | RELATIONSHIP
    source_ids: list[str] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)  # IDs of related nodes
    created_at: str = field(default_factory=_now)
    last_reinforced: str = field(default_factory=_now)
    last_accessed: str = field(default_factory=_now)
    access_count: int = 0
    reinforcement_count: int = 0
    is_archived: bool = False
    is_deleted: bool = False


@dataclass
class ConsolidationReport:
    """Result of a consolidation cycle."""
    report_id: str = field(default_factory=_uuid)
    date: str = field(default_factory=_now)
    nodes_decayed: int = 0
    nodes_compressed: int = 0
    nodes_pruned: int = 0
    nodes_reinforced: int = 0
    total_nodes: int = 0
    avg_confidence: float = 0.0


@dataclass
class DomainStatus:
    """Status of a knowledge domain."""
    domain: str = ""
    subdomains: list[dict[str, Any]] = field(default_factory=list)
    total_confidence: float = 0.0
    coverage: str = "NONE"  # HIGH | MEDIUM | LOW | NONE
    active_gaps: int = 0
    knowledge_count: int = 0
    last_updated: str = ""


@dataclass
class AuditEntry:
    """A logged decision in the audit trail."""
    entry_id: str = field(default_factory=_uuid)
    timestamp: str = field(default_factory=_now)
    action: AuditAction = AuditAction.OBSERVE
    target_id: str = ""  # ID of the related entity
    details: dict[str, Any] = field(default_factory=dict)
