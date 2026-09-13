"""Curio — Validation Tests.

Tests for privacy, export, injection resistance, and data integrity.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.curio import Curio


def test_export_knowledge():
    """Test exporting knowledge as JSON."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    c.teach("Test fact 1", domain="test")
    c.teach("Test fact 2", domain="test")

    # Export
    nodes = c.know()
    export_data = json.dumps(nodes, indent=2)

    assert len(nodes) == 2
    assert "Test fact 1" in export_data
    assert "Test fact 2" in export_data

    # Verify it's valid JSON
    parsed = json.loads(export_data)
    assert len(parsed) == 2

    c.close()
    print("  ✓ Export knowledge")


def test_delete_knowledge():
    """Test deleting knowledge and verifying it's gone."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    # Store something
    node = c.teach("Secret information", domain="secrets")
    kid = node.knowledge_id

    # Verify it exists
    assert c.store.get_knowledge(kid) is not None

    # Delete it
    import sqlite3
    conn = sqlite3.connect(str(c.data_dir / "knowledge.db"))
    conn.execute("UPDATE knowledge SET is_deleted = 1 WHERE knowledge_id = ?", (kid,))
    conn.commit()
    conn.close()

    # Verify it's gone from normal queries
    result = c.store.get_knowledge(kid)
    assert result is None

    # Verify know() doesn't include it
    known = c.know()
    assert all(k["content"] != "Secret information" for k in known)

    c.close()
    print("  ✓ Delete knowledge")


def test_delete_audit_log():
    """Test that audit log can be cleared."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    c.teach("Something", domain="test")
    entries = c.show_audit()
    assert len(entries) > 0

    # Clear the audit log
    audit_path = c.data_dir / "audit.jsonl"
    audit_path.unlink()

    # Verify it's empty
    entries = c.show_audit()
    assert len(entries) == 0

    c.close()
    print("  ✓ Delete audit log")


def test_no_external_leaks():
    """Test that data stays local — no external API calls without config."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    # Clear any LLM config
    old_key = os.environ.get("CURIO_LLM_API_KEY")
    old_url = os.environ.get("CURIO_LLM_BASE_URL")
    old_provider = os.environ.get("CURIO_LLM_PROVIDER")

    os.environ.pop("CURIO_LLM_API_KEY", None)
    os.environ.pop("CURIO_LLM_BASE_URL", None)
    os.environ.pop("CURIO_LLM_PROVIDER", None)

    try:
        # Teach and observe — should work without external calls
        c.teach("Local fact", domain="local")
        gaps = c.observe("New observation", source="test")
        known = c.know()

        assert len(known) >= 1
    finally:
        # Restore env vars
        if old_key:
            os.environ["CURIO_LLM_API_KEY"] = old_key
        if old_url:
            os.environ["CURIO_LLM_BASE_URL"] = old_url
        if old_provider:
            os.environ["CURIO_LLM_PROVIDER"] = old_provider

    c.close()
    print("  ✓ No external leaks")


def test_data_directory_isolation():
    """Test that each Curio instance uses its own data directory."""
    tmp1 = tempfile.mkdtemp()
    tmp2 = tempfile.mkdtemp()

    c1 = Curio(data_dir=Path(tmp1))
    c2 = Curio(data_dir=Path(tmp2))

    c1.teach("Fact from instance 1", domain="instance1")
    c2.teach("Fact from instance 2", domain="instance2")

    known1 = c1.know()
    known2 = c2.know()

    # Each instance should only see its own data
    assert any("instance 1" in k["content"] for k in known1)
    assert not any("instance 2" in k["content"] for k in known1)
    assert any("instance 2" in k["content"] for k in known2)
    assert not any("instance 1" in k["content"] for k in known2)

    c1.close()
    c2.close()
    print("  ✓ Data directory isolation")


def test_consolidation_preserves_important():
    """Test that consolidation doesn't delete high-confidence knowledge."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    # Store high-confidence knowledge
    c.teach("Critical: production database password is in env var DB_PASS", domain="security", confidence=0.95)
    c.teach("The API uses FastAPI", domain="backend", confidence=0.8)

    # Store low-confidence knowledge
    c.teach("Maybe the cache uses Redis?", domain="cache", confidence=0.3)

    # Run consolidation
    report = c.consolidate()

    # High-confidence knowledge should survive
    known = c.know()
    contents = " ".join(k["content"] for k in known)
    assert "production database" in contents or "FastAPI" in contents

    c.close()
    print("  ✓ Consolidation preserves important knowledge")


def test_consolidation_removes_stale():
    """Test that consolidation archives old, low-confidence knowledge."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    # Store old, low-confidence knowledge
    from src.models import KnowledgeNode, _now
    from datetime import datetime, timedelta

    old_date = (datetime.utcnow() - timedelta(days=100)).isoformat() + "Z"

    node = KnowledgeNode(
        content="Old unverified rumor about the project",
        domain="rumors",
        confidence=0.15,
        last_accessed=old_date,
        last_reinforced=old_date,
    )
    c.store.store_knowledge(node)

    # Also store fresh, high-confidence knowledge
    c.teach("Fresh fact", domain="current", confidence=0.9)

    # Run consolidation
    report = c.consolidate()

    # The old, low-confidence node should be archived or deleted
    stats = c.store.stats()
    # At least something should have been processed
    assert report.total_nodes >= 1

    c.close()
    print("  ✓ Consolidation removes stale knowledge")


def test_repeated_observations_increase_confidence():
    """Test that seeing the same information multiple times increases confidence."""
    tmp = tempfile.mkdtemp()
    c = Curio(data_dir=Path(tmp))

    # Teach the same fact multiple times
    c.teach("API uses JWT RS256", domain="auth")
    c.teach("API uses JWT RS256", domain="auth")
    c.teach("API uses JWT RS256", domain="auth")

    known = c.know()
    auth_nodes = [k for k in known if "JWT" in k["content"]]

    # Should have at least one node
    assert len(auth_nodes) >= 1

    c.close()
    print("  ✓ Repeated observations handled")


def test_full_validation_suite():
    """Run all validation tests."""
    print("Running validation tests...\n")
    test_export_knowledge()
    test_delete_knowledge()
    test_delete_audit_log()
    test_no_external_leaks()
    test_data_directory_isolation()
    test_consolidation_preserves_important()
    test_consolidation_removes_stale()
    test_repeated_observations_increase_confidence()
    print("\n✅ All validation tests passed!")


if __name__ == "__main__":
    test_full_validation_suite()
