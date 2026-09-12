"""Curio — Autonomous Learning Agent.

AI that knows what it doesn't know — and learns it.
"""

from .curio import Curio
from .models import (
    Appraisal, ConsolidationReport, DomainStatus, Gap, GapType,
    KnowledgeNode, LearningDecision, Observation, ObservationType,
    Priority, RawInfo, SourceRecord,
)

__version__ = "0.1.0"

__all__ = [
    "Curio",
    "Appraisal",
    "ConsolidationReport",
    "DomainStatus",
    "Gap",
    "GapType",
    "KnowledgeNode",
    "LearningDecision",
    "Observation",
    "ObservationType",
    "Priority",
    "RawInfo",
    "SourceRecord",
]
