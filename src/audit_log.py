"""Curio — Audit Log.

Records every learning decision for transparency and debugging.
Append-only JSONL file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AuditAction, AuditEntry, _now, _uuid


class AuditLog:
    """Append-only audit trail for all learning decisions."""

    def __init__(self, path: str | Path = "~/.curio/audit.jsonl"):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        action: AuditAction,
        target_id: str = "",
        **details: Any,
    ) -> AuditEntry:
        """Record an audit entry."""
        entry = AuditEntry(
            entry_id=_uuid(),
            timestamp=_now(),
            action=action,
            target_id=target_id,
            details=details,
        )
        with open(self.path, "a") as f:
            f.write(json.dumps({
                "entry_id": entry.entry_id,
                "timestamp": entry.timestamp,
                "action": entry.action.value,
                "target_id": entry.target_id,
                "details": entry.details,
            }) + "\n")
        return entry

    def read(self, last_n: int | None = None) -> list[dict[str, Any]]:
        """Read audit entries, optionally the last N."""
        if not self.path.exists():
            return []
        entries = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        if last_n is not None:
            entries = entries[-last_n:]
        return entries

    def count(self) -> int:
        """Total number of audit entries."""
        if not self.path.exists():
            return 0
        with open(self.path) as f:
            return sum(1 for line in f if line.strip())
