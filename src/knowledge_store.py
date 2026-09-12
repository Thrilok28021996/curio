"""Curio — Knowledge Store.

SQLite-backed storage for knowledge nodes, sources, and gaps.
Provides vector similarity search via embeddings.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import (
    Gap, GapType, KnowledgeNode, Priority, SourceRecord,
    _now, _uuid,
)


class KnowledgeStore:
    """SQLite-backed knowledge graph with vector search."""

    def __init__(self, db_path: str | Path = "~/.curio/knowledge.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """Create tables if they don't exist."""
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                knowledge_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                domain TEXT DEFAULT '',
                subdomain TEXT DEFAULT '',
                confidence REAL DEFAULT 0.5,
                node_type TEXT DEFAULT 'FACT',
                source_ids TEXT DEFAULT '[]',
                connections TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                last_reinforced TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                reinforcement_count INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                embedding BLOB
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT DEFAULT '',
                trust_score REAL DEFAULT 0.5,
                reliability TEXT DEFAULT 'SECONDARY',
                last_verified TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                accuracy_history TEXT DEFAULT '[]'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS gaps (
                gap_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                topic TEXT NOT NULL,
                description TEXT DEFAULT '',
                confidence REAL DEFAULT 0.5,
                priority TEXT DEFAULT 'MEDIUM',
                source_observation TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS domain_map (
                domain TEXT PRIMARY KEY,
                subdomains TEXT DEFAULT '[]',
                total_confidence REAL DEFAULT 0.0,
                coverage TEXT DEFAULT 'NONE',
                active_gaps INTEGER DEFAULT 0,
                knowledge_count INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT ''
            )
        """)

        self.conn.commit()

    # ----------------------------------------------------------
    # Knowledge nodes
    # ----------------------------------------------------------

    def store_knowledge(self, node: KnowledgeNode) -> KnowledgeNode:
        """Store or update a knowledge node."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO knowledge
            (knowledge_id, content, domain, subdomain, confidence, node_type,
             source_ids, connections, created_at, last_reinforced, last_accessed,
             access_count, reinforcement_count, is_archived, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            node.knowledge_id, node.content, node.domain, node.subdomain,
            node.confidence, node.node_type,
            json.dumps(node.source_ids), json.dumps(node.connections),
            node.created_at, node.last_reinforced, node.last_accessed,
            node.access_count, node.reinforcement_count,
            int(node.is_archived), int(node.is_deleted),
        ))
        self.conn.commit()
        return node

    def get_knowledge(self, knowledge_id: str) -> KnowledgeNode | None:
        """Retrieve a knowledge node by ID."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM knowledge WHERE knowledge_id = ? AND is_deleted = 0",
            (knowledge_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_node(row)

    def search_knowledge(
        self,
        domain: str = "",
        min_confidence: float = 0.0,
        include_archived: bool = False,
    ) -> list[KnowledgeNode]:
        """Search knowledge nodes by domain and confidence."""
        cur = self.conn.cursor()
        query = "SELECT * FROM knowledge WHERE is_deleted = 0"
        params: list[Any] = []

        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if min_confidence > 0:
            query += " AND confidence >= ?"
            params.append(min_confidence)
        if not include_archived:
            query += " AND is_archived = 0"

        query += " ORDER BY confidence DESC, last_accessed DESC"
        cur.execute(query, params)
        return [self._row_to_node(row) for row in cur.fetchall()]

    def count_knowledge(self, domain: str = "") -> int:
        """Count active knowledge nodes."""
        cur = self.conn.cursor()
        if domain:
            cur.execute(
                "SELECT COUNT(*) FROM knowledge WHERE is_deleted = 0 AND domain = ?",
                (domain,),
            )
        else:
            cur.execute(
                "SELECT COUNT(*) FROM knowledge WHERE is_deleted = 0"
            )
        return cur.fetchone()[0]

    def _row_to_node(self, row: sqlite3.Row) -> KnowledgeNode:
        """Convert a database row to a KnowledgeNode."""
        return KnowledgeNode(
            knowledge_id=row["knowledge_id"],
            content=row["content"],
            domain=row["domain"],
            subdomain=row["subdomain"],
            confidence=row["confidence"],
            node_type=row["node_type"],
            source_ids=json.loads(row["source_ids"]),
            connections=json.loads(row["connections"]),
            created_at=row["created_at"],
            last_reinforced=row["last_reinforced"],
            last_accessed=row["last_accessed"],
            access_count=row["access_count"],
            reinforcement_count=row["reinforcement_count"],
            is_archived=bool(row["is_archived"]),
            is_deleted=bool(row["is_deleted"]),
        )

    # ----------------------------------------------------------
    # Sources
    # ----------------------------------------------------------

    def store_source(self, source: SourceRecord) -> SourceRecord:
        """Store or update a source record."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO sources
            (source_id, url, title, trust_score, reliability,
             last_verified, access_count, accuracy_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source.source_id, source.url, source.title,
            source.trust_score, source.reliability,
            source.last_verified, source.access_count,
            json.dumps(source.accuracy_history),
        ))
        self.conn.commit()
        return source

    def get_source(self, source_id: str) -> SourceRecord | None:
        """Retrieve a source by ID."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM sources WHERE source_id = ?", (source_id,))
        row = cur.fetchone()
        if not row:
            return None
        return SourceRecord(
            source_id=row["source_id"],
            url=row["url"],
            title=row["title"],
            trust_score=row["trust_score"],
            reliability=row["reliability"],
            last_verified=row["last_verified"],
            access_count=row["access_count"],
            accuracy_history=json.loads(row["accuracy_history"]),
        )

    # ----------------------------------------------------------
    # Gaps
    # ----------------------------------------------------------

    def store_gap(self, gap: Gap) -> Gap:
        """Store a gap record."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO gaps
            (gap_id, type, topic, description, confidence, priority,
             source_observation, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gap.gap_id, gap.type.value, gap.topic, gap.description,
            gap.confidence, gap.priority.value,
            gap.source_observation, gap.created_at, gap.status,
        ))
        self.conn.commit()
        return gap

    def get_open_gaps(self, priority: str = "") -> list[Gap]:
        """Get all open gaps, optionally filtered by priority."""
        cur = self.conn.cursor()
        query = "SELECT * FROM gaps WHERE status = 'OPEN'"
        params: list[Any] = []
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        query += " ORDER BY created_at DESC"
        cur.execute(query, params)
        return [self._row_to_gap(row) for row in cur.fetchall()]

    def update_gap_status(self, gap_id: str, status: str):
        """Update a gap's status."""
        cur = self.conn.cursor()
        cur.execute("UPDATE gaps SET status = ? WHERE gap_id = ?", (status, gap_id))
        self.conn.commit()

    def _row_to_gap(self, row: sqlite3.Row) -> Gap:
        """Convert a database row to a Gap."""
        return Gap(
            gap_id=row["gap_id"],
            type=GapType(row["type"]),
            topic=row["topic"],
            description=row["description"],
            confidence=row["confidence"],
            priority=Priority(row["priority"]),
            source_observation=row["source_observation"],
            created_at=row["created_at"],
            status=row["status"],
        )

    # ----------------------------------------------------------
    # Domain map
    # ----------------------------------------------------------

    def update_domain_map(
        self,
        domain: str,
        knowledge_count: int = 0,
        active_gaps: int = 0,
        total_confidence: float = 0.0,
    ):
        """Update domain coverage stats."""
        coverage = "NONE"
        if total_confidence > 0.8 and active_gaps == 0:
            coverage = "HIGH"
        elif total_confidence > 0.5:
            coverage = "MEDIUM"
        elif total_confidence > 0:
            coverage = "LOW"

        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO domain_map
            (domain, total_confidence, coverage, active_gaps,
             knowledge_count, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (domain, total_confidence, coverage, active_gaps,
              knowledge_count, _now()))
        self.conn.commit()

    def get_domain_map(self) -> list[dict[str, Any]]:
        """Get all domain coverage stats."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM domain_map ORDER BY total_confidence DESC")
        return [dict(row) for row in cur.fetchall()]

    # ----------------------------------------------------------
    # Maintenance
    # ----------------------------------------------------------

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def stats(self) -> dict[str, Any]:
        """Return store statistics."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM knowledge WHERE is_deleted = 0")
        total_knowledge = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM knowledge WHERE is_deleted = 0 AND is_archived = 1")
        archived = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM gaps WHERE status = 'OPEN'")
        open_gaps = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM sources")
        total_sources = cur.fetchone()[0]
        cur.execute(
            "SELECT AVG(confidence) FROM knowledge WHERE is_deleted = 0 AND is_archived = 0"
        )
        avg_conf = cur.fetchone()[0] or 0.0

        return {
            "total_knowledge": total_knowledge,
            "active_knowledge": total_knowledge - archived,
            "archived_knowledge": archived,
            "open_gaps": open_gaps,
            "total_sources": total_sources,
            "avg_confidence": round(avg_conf, 3),
        }
