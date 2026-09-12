"""Curio MCP Server — Model Context Protocol interface for Curio.

Exposes Curio's learning capabilities as MCP tools that can be used
with Claude Code, Cursor, and other MCP-compatible clients.

Usage:
    python -m src.mcp_server
    # or
    python src/mcp_server.py

The server runs on stdio transport (default for MCP).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

# Import Curio from the src package
try:
    from .curio import Curio
except ImportError:
    # Running directly as a script
    from curio import Curio

# Create the MCP server
server = MCPServer(
    name="curio",
    version="0.1.0",
    description="Curio — Autonomous Learning Agent MCP Server. "
    "Exposes learning, observation, knowledge retrieval, and "
    "consolidation capabilities as MCP tools.",
    instructions=(
        "This server provides tools for interacting with Curio, "
        "an autonomous learning AI agent. You can teach Curio facts, "
        "process observations, query what it knows, check knowledge gaps, "
        "view learning progress, assess confidence on topics, and "
        "run memory consolidation cycles."
    ),
)

# Shared Curio instance
_curio: Curio | None = None


def _get_curio() -> Curio:
    """Get or create the Curio instance."""
    global _curio
    if _curio is None:
        _curio = Curio()
    return _curio


# -------------------------------------------------------------------
# Tool definitions
# -------------------------------------------------------------------


@server.tool(
    name="curio_teach",
    description=(
        "Teach Curio something directly. Stores a knowledge fact "
        "bypassing the learning loop. Use this when you have a specific "
        "fact, preference, or piece of knowledge Curio should know."
    ),
)
def curio_teach(
    content: str,
    domain: str = "",
    confidence: float = 0.8,
) -> str:
    """Teach Curio something directly.

    Args:
        content: The fact or knowledge to teach.
        domain: Optional domain category (e.g. "Python", "DevOps").
        confidence: Confidence level 0.0-1.0 (default 0.8).

    Returns:
        JSON string with the stored knowledge node details.
    """
    curio = _get_curio()
    node = curio.teach(content=content, domain=domain, confidence=confidence)
    return json.dumps(
        {
            "status": "success",
            "knowledge_id": node.knowledge_id,
            "domain": node.domain,
            "confidence": node.confidence,
            "content": node.content,
            "node_type": node.node_type,
            "created_at": node.created_at,
        },
        indent=2,
    )


@server.tool(
    name="curio_observe",
    description=(
        "Process an observation through Curio's full learning loop. "
        "The observation is analyzed for knowledge gaps, and Curio "
        "may automatically research and learn from the information."
    ),
)
def curio_observe(
    content: str,
    source: str = "",
    obs_type: str = "event",
) -> str:
    """Process an observation and detect knowledge gaps.

    Args:
        content: The observation content to process.
        source: Optional source attribution.
        obs_type: Observation type — one of: query, event, document,
            conversation, error, system. Default: event.

    Returns:
        JSON string with gaps detected during observation.
    """
    curio = _get_curio()
    gaps = curio.observe(content=content, source=source, obs_type=obs_type)
    return json.dumps(
        {
            "status": "success",
            "gaps_detected": len(gaps),
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "type": g.type.value,
                    "topic": g.topic,
                    "description": g.description,
                    "priority": g.priority.value,
                    "status": g.status,
                }
                for g in gaps
            ],
        },
        indent=2,
    )


@server.tool(
    name="curio_know",
    description=(
        "Retrieve what Curio knows, ranked by confidence. "
        "Returns the most confident knowledge items."
    ),
)
def curio_know(top_n: int = 10) -> str:
    """Retrieve what Curio knows.

    Args:
        top_n: Number of top knowledge items to return (default 10).

    Returns:
        JSON string with ranked knowledge items.
    """
    curio = _get_curio()
    items = curio.know(top_n=top_n)
    return json.dumps(
        {
            "status": "success",
            "count": len(items),
            "items": items,
        },
        indent=2,
    )


@server.tool(
    name="curio_gaps",
    description=(
        "Show Curio's open knowledge gaps — topics where Curio "
        "needs more information."
    ),
)
def curio_gaps() -> str:
    """Show knowledge gaps.

    Returns:
        JSON string with open knowledge gaps.
    """
    curio = _get_curio()
    gaps = curio.gaps()
    return json.dumps(
        {
            "status": "success",
            "count": len(gaps),
            "gaps": gaps,
        },
        indent=2,
    )


@server.tool(
    name="curio_progress",
    description=(
        "Show Curio's learning progress and coverage report. "
        "Includes domain breakdown, coverage levels, and statistics."
    ),
)
def curio_progress() -> str:
    """Show learning progress.

    Returns:
        JSON string with progress and coverage data.
    """
    curio = _get_curio()
    progress = curio.progress()
    return json.dumps(
        {
            "status": "success",
            "progress": progress,
        },
        indent=2,
    )


@server.tool(
    name="curio_confidence",
    description=(
        "Check Curio's confidence level about a specific topic. "
        "Returns a confidence score from 0.0 to 1.0."
    ),
)
def curio_confidence(topic: str) -> str:
    """Check confidence about a topic.

    Args:
        topic: The topic to check confidence for.

    Returns:
        JSON string with confidence score.
    """
    curio = _get_curio()
    score = curio.confidence(topic)
    return json.dumps(
        {
            "status": "success",
            "topic": topic,
            "confidence": score,
            "level": (
                "high" if score >= 0.7
                else "medium" if score >= 0.4
                else "low"
            ),
        },
        indent=2,
    )


@server.tool(
    name="curio_consolidate",
    description=(
        "Run a forgetting/consolidation cycle on Curio's memory. "
        "Decays confidence, compresses related knowledge, and prunes "
        "low-confidence items."
    ),
)
def curio_consolidate() -> str:
    """Run a consolidation cycle.

    Returns:
        JSON string with the consolidation report.
    """
    curio = _get_curio()
    report = curio.consolidate()
    return json.dumps(
        {
            "status": "success",
            "report": {
                "report_id": report.report_id,
                "date": report.date,
                "nodes_decayed": report.nodes_decayed,
                "nodes_compressed": report.nodes_compressed,
                "nodes_pruned": report.nodes_pruned,
                "nodes_reinforced": report.nodes_reinforced,
                "total_nodes": report.total_nodes,
                "avg_confidence": report.avg_confidence,
            },
        },
        indent=2,
    )


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------


def main():
    """Run the MCP server on stdio transport."""
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
