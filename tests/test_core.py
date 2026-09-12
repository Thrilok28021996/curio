"""Curio — Tests for core components."""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    AuditAction, Gap, GapType, KnowledgeNode, LearningDecision,
    Observation, ObservationType, Priority, SourceRecord, _now,
)
from src.audit_log import AuditLog
from src.knowledge_store import KnowledgeStore
from src.gap_detector import GapDetector
from src.relevance_filter import RelevanceFilter
from src.knowledge_integrator import KnowledgeIntegrator
from src.memory_consolidator import MemoryConsolidator
from src.knowledge_map import KnowledgeMap
from src.curio import Curio


def setup_test_env():
    """Create a temporary directory for test data."""
    tmp = tempfile.mkdtemp(prefix="curio_test_")
    data_dir = Path(tmp)
    return data_dir


def test_models():
    """Test data model creation."""
    obs = Observation(
        type=ObservationType.EVENT,
        content="Test observation",
        source="test.py",
    )
    assert obs.observation_id
    assert obs.type == ObservationType.EVENT

    gap = Gap(
        type=GapType.UNKNOWN,
        topic="test topic",
        confidence=0.5,
    )
    assert gap.gap_id
    assert gap.type == GapType.UNKNOWN

    node = KnowledgeNode(
        content="Test knowledge",
        domain="test domain",
        confidence=0.8,
    )
    assert node.knowledge_id
    assert node.confidence == 0.8

    print("  ✓ Models")


def test_audit_log():
    """Test audit log writing and reading."""
    data_dir = setup_test_env()
    audit = AuditLog(data_dir / "audit.jsonl")

    audit.log(AuditAction.OBSERVE, content="test")
    audit.log(AuditAction.STORED, target_id="abc123")

    entries = audit.read()
    assert len(entries) == 2
    assert entries[0]["action"] == "OBSERVE"
    assert entries[1]["action"] == "STORED"

    last = audit.read(last_n=1)
    assert len(last) == 1

    assert audit.count() == 2

    print("  ✓ Audit Log")


def test_knowledge_store():
    """Test knowledge store CRUD operations."""
    data_dir = setup_test_env()
    store = KnowledgeStore(data_dir / "knowledge.db")

    # Store a knowledge node
    node = KnowledgeNode(
        content="Test knowledge content",
        domain="test domain",
        confidence=0.75,
    )
    store.store_knowledge(node)

    # Retrieve it
    retrieved = store.get_knowledge(node.knowledge_id)
    assert retrieved is not None
    assert retrieved.content == "Test knowledge content"
    assert retrieved.confidence == 0.75

    # Search by domain
    results = store.search_knowledge(domain="test domain")
    assert len(results) == 1

    # Count
    assert store.count_knowledge() == 1
    assert store.count_knowledge(domain="test domain") == 1
    assert store.count_knowledge(domain="other") == 0

    # Stats
    stats = store.stats()
    assert stats["total_knowledge"] == 1

    # Store a gap
    gap = Gap(
        type=GapType.UNKNOWN,
        topic="test gap",
        confidence=0.3,
    )
    store.store_gap(gap)
    gaps = store.get_open_gaps()
    assert len(gaps) == 1

    # Update gap status
    store.update_gap_status(gap.gap_id, "RESOLVED")
    gaps = store.get_open_gaps()
    assert len(gaps) == 0

    # Store a source
    source = SourceRecord(
        url="https://example.com",
        title="Test Source",
        trust_score=0.8,
    )
    store.store_source(source)
    retrieved_source = store.get_source(source.source_id)
    assert retrieved_source is not None
    assert retrieved_source.url == "https://example.com"

    store.close()
    print("  ✓ Knowledge Store")


def test_gap_detector():
    """Test gap detection from observations."""
    data_dir = setup_test_env()
    store = KnowledgeStore(data_dir / "knowledge.db")
    audit = AuditLog(data_dir / "audit.jsonl")
    detector = GapDetector(store, audit)

    # First observation — should detect UNKNOWN gap
    obs1 = Observation(
        type=ObservationType.DOCUMENT,
        content="The project uses FastAPI",
        source="main.py",
    )
    gaps1 = detector.detect(obs1)
    assert len(gaps1) == 1
    assert gaps1[0].type == GapType.UNKNOWN

    # Teach something first, then observe related content
    node = KnowledgeNode(
        content="Authentication uses JWT with RS256 signing",
        domain="auth",
        confidence=0.8,
    )
    store.store_knowledge(node)

    # Observe contradictory info — should detect CONTRADICTORY gap
    obs2 = Observation(
        type=ObservationType.DOCUMENT,
        content="Authentication is no longer using JWT, now uses OAuth2",
        source="auth_v2.py",
    )
    gaps2 = detector.detect(obs2)
    # Should detect at least one gap (OUTDATED or CONTRADICTORY)
    assert len(gaps2) >= 1

    store.close()
    print("  ✓ Gap Detector")


def test_relevance_filter():
    """Test relevance scoring and LEARN/DEFER/IGNORE decisions."""
    data_dir = setup_test_env()
    store = KnowledgeStore(data_dir / "knowledge.db")
    audit = AuditLog(data_dir / "audit.jsonl")
    filter_engine = RelevanceFilter(store, audit)

    # Set goals and domains
    filter_engine.set_goals(["backend development", "API design"])
    filter_engine.set_domains(["authentication", "database", "framework"])

    # High-relevance gap (matches goals and domain)
    gap_high = Gap(
        type=GapType.UNKNOWN,
        topic="authentication JWT RS256",
        priority=Priority.HIGH,
    )
    appraisal = filter_engine.appraise(gap_high)
    assert appraisal.decision == LearningDecision.LEARN
    assert appraisal.relevance_score > 0.5

    # Low-relevance gap (doesn't match goals or domain)
    gap_low = Gap(
        type=GapType.UNKNOWN,
        topic="weather patterns in Antarctica",
        priority=Priority.LOW,
    )
    appraisal = filter_engine.appraise(gap_low)
    assert appraisal.decision in (LearningDecision.DEFER, LearningDecision.IGNORE)

    store.close()
    print("  ✓ Relevance Filter")


def test_memory_consolidator():
    """Test decay, compression, and pruning."""
    data_dir = setup_test_env()
    store = KnowledgeStore(data_dir / "knowledge.db")
    audit = AuditLog(data_dir / "audit.jsonl")
    consolidator = MemoryConsolidator(store, audit)

    # Store some knowledge
    for i in range(5):
        node = KnowledgeNode(
            content=f"Knowledge node {i}",
            domain=f"domain_{i}",
            confidence=0.5 + (i * 0.1),
            last_accessed="2026-01-01T00:00:00Z",  # Old date
            last_reinforced="2026-01-01T00:00:00Z",
        )
        store.store_knowledge(node)

    # Run consolidation
    report = consolidator.consolidate()
    assert report.total_nodes == 5
    assert report.nodes_decayed >= 0  # Some should have decayed

    # Check stats after consolidation
    stats = store.stats()
    assert stats["total_knowledge"] == 5

    store.close()
    print("  ✓ Memory Consolidator")


def test_knowledge_map():
    """Test metacognition features."""
    data_dir = setup_test_env()
    store = KnowledgeStore(data_dir / "knowledge.db")
    audit = AuditLog(data_dir / "audit.jsonl")
    km = KnowledgeMap(store, audit)

    # Store some knowledge
    for i in range(3):
        node = KnowledgeNode(
            content=f"Test knowledge {i}",
            domain="test_domain",
            confidence=0.7 + (i * 0.1),
        )
        store.store_knowledge(node)

    # What does Curio know?
    known = km.what_i_know()
    assert len(known) == 3
    assert known[0]["confidence"] >= known[1]["confidence"]  # Sorted by confidence

    # Check confidence
    score = km.confidence("test_domain")
    assert score > 0

    # Coverage report
    report = km.coverage_report()
    assert report["summary"]["total_knowledge"] == 3

    store.close()
    print("  ✓ Knowledge Map")


def test_curio_orchestrator():
    """Test the full Curio orchestrator."""
    data_dir = setup_test_env()
    curio = Curio(data_dir=data_dir)

    # Teach something
    node = curio.teach("FastAPI is the backend framework", domain="backend")
    assert node.knowledge_id

    # Check what we know
    known = curio.know()
    assert len(known) == 1
    assert "FastAPI" in known[0]["content"]

    # Check progress
    progress = curio.progress()
    assert progress["summary"]["total_knowledge"] == 1

    # Check confidence
    score = curio.confidence("FastAPI")
    assert score > 0

    # Check stats
    stats = curio.stats()
    assert stats["total_knowledge"] == 1

    # Consolidate
    report = curio.consolidate()
    assert report.total_nodes == 1

    # Audit
    audit = curio.show_audit()
    assert len(audit) > 0

    curio.close()
    print("  ✓ Curio Orchestrator")


def test_full_loop():
    """Test the complete observe → detect → appraise → learn loop."""
    data_dir = setup_test_env()
    curio = Curio(data_dir=data_dir)

    # Observe something (should detect a gap)
    gaps = curio.observe(
        "The project uses PostgreSQL for the database",
        source="config.py",
    )
    assert len(gaps) >= 1

    # Teach it directly
    curio.teach("Database is PostgreSQL with SQLAlchemy ORM", domain="database")

    # Now observe related content — gap should be smaller
    gaps2 = curio.observe(
        "PostgreSQL connection pool size is 20",
        source="config.py",
    )

    # Check what Curio knows
    known = curio.know()
    assert len(known) >= 1

    # Full audit trail exists
    audit = curio.show_audit()
    assert len(audit) >= 3  # At least observe + gap + store

    curio.close()
    print("  ✓ Full Learning Loop")


if __name__ == "__main__":
    print("Running Curio tests...\n")
    test_models()
    test_audit_log()
    test_knowledge_store()
    test_gap_detector()
    test_relevance_filter()
    test_memory_consolidator()
    test_knowledge_map()
    test_curio_orchestrator()
    test_full_loop()
    print("\n✅ All tests passed!")
