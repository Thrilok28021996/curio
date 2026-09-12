"""Curio CLI — Command-line interface.

Usage:
    python -m curio observe "The API uses JWT RS256 auth"
    python -m curio gaps
    python -m curio know
    python -m curio progress
    python -m curio confidence "JWT authentication"
    python -m curio consolidate
    python -m curio audit --last 10
    python -m curio stats
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from typing import Any

from .curio import Curio


def _print_json(data: Any):
    """Pretty-print JSON output."""
    print(json.dumps(data, indent=2, default=str))


def cmd_observe(args, curio: Curio):
    """Process an observation."""
    gaps = curio.observe(
        content=args.content,
        source=args.source or "",
        obs_type=args.type or "event",
    )
    if gaps:
        print(f"Detected {len(gaps)} gap(s):")
        for gap in gaps:
            print(f"  [{gap.priority.value}] {gap.type.value}: {gap.topic}")
    else:
        print("No gaps detected.")


def cmd_teach(args, curio: Curio):
    """Directly teach Curio something."""
    node = curio.teach(
        content=args.content,
        domain=args.domain or "",
        confidence=args.confidence,
    )
    print(f"Stored knowledge: {node.knowledge_id[:8]}...")
    print(f"  Domain: {node.domain}")
    print(f"  Confidence: {node.confidence:.2f}")


def cmd_gaps(args, curio: Curio):
    """Show open knowledge gaps."""
    gaps = curio.gaps(priority=args.priority or "")
    if not gaps:
        print("No open gaps. Curio knows everything it needs to.")
        return
    print(f"Open gaps: {len(gaps)}\n")
    for g in gaps:
        print(f"  [{g['priority']}] {g['type']}: {g['topic']}")
        print(f"    created: {g['created']}")
        print()


def cmd_know(args, curio: Curio):
    """Show what Curio knows."""
    items = curio.know(top_n=args.top or 10)
    if not items:
        print("Curio hasn't learned anything yet.")
        return
    print(f"Top {len(items)} knowledge nodes:\n")
    for i, item in enumerate(items, 1):
        print(f"  {i}. [{item['confidence']:.2f}] {item['content']}")
        print(f"     domain: {item['domain']} | sources: {item['sources']}")
        print()


def cmd_progress(args, curio: Curio):
    """Show learning progress."""
    report = curio.progress()
    summary = report["summary"]
    print("Curio Progress Report")
    print("=" * 40)
    print(f"  Active knowledge:  {summary['active_knowledge']}")
    print(f"  Archived:          {summary['archived_knowledge']}")
    print(f"  Open gaps:         {summary['open_gaps']}")
    print(f"  Sources tracked:   {summary['total_sources']}")
    print(f"  Avg confidence:    {summary['avg_confidence']:.3f}")
    print()

    if report["domains"]:
        print("Domains:")
        for d in report["domains"]:
            print(f"  {d['domain']}: {d['coverage']} "
                  f"({d['knowledge_count']} nodes, "
                  f"{d['active_gaps']} gaps)")
    print()

    gaps = report["gaps"]
    print(f"Gaps: {gaps['total']} total "
          f"({gaps['high']} high, {gaps['medium']} medium, "
          f"{gaps['low']} low)")


def cmd_confidence(args, curio: Curio):
    """Check confidence about a topic."""
    score = curio.confidence(args.topic)
    print(f"Confidence about '{args.topic}': {score:.3f}")


def cmd_consolidate(args, curio: Curio):
    """Run consolidation cycle."""
    report = curio.consolidate()
    print("Consolidation complete:")
    print(f"  Decayed:     {report.nodes_decayed}")
    print(f"  Compressed:  {report.nodes_compressed}")
    print(f"  Pruned:      {report.nodes_pruned}")
    print(f"  Reinforced:  {report.nodes_reinforced}")
    print(f"  Total nodes: {report.total_nodes}")
    print(f"  Avg confidence: {report.avg_confidence:.3f}")


def cmd_audit(args, curio: Curio):
    """Show audit log."""
    entries = curio.show_audit(last_n=args.last or 20)
    if not entries:
        print("No audit entries.")
        return
    print(f"Last {len(entries)} audit entries:\n")
    for e in entries:
        print(f"  {e['timestamp']} | {e['action']} | "
              f"target={e['target_id'][:8]}...")
        if e.get("details"):
            for k, v in e["details"].items():
                print(f"    {k}: {v}")
        print()


def cmd_stats(args, curio: Curio):
    """Show store statistics."""
    stats = curio.stats()
    print("Curio Store Stats")
    print("=" * 40)
    for k, v in stats.items():
        print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        prog="curio",
        description="Curio — AI that knows what it doesn't know.",
    )
    sub = parser.add_subparsers(dest="command")

    # teach
    p_teach = sub.add_parser("teach", help="Directly teach Curio something")
    p_teach.add_argument("content", help="What to teach")
    p_teach.add_argument("--domain", help="Domain/topic")
    p_teach.add_argument("--confidence", type=float, default=0.8, help="Initial confidence")

    # observe
    p_obs = sub.add_parser("observe", help="Process an observation")
    p_obs.add_argument("content", help="Observation content")
    p_obs.add_argument("--source", help="Source of the observation")
    p_obs.add_argument("--type", help="Observation type")

    # gaps
    p_gaps = sub.add_parser("gaps", help="Show open knowledge gaps")
    p_gaps.add_argument("--priority", help="Filter by priority")

    # know
    p_know = sub.add_parser("know", help="Show what Curio knows")
    p_know.add_argument("--top", type=int, help="Number of results")

    # progress
    sub.add_parser("progress", help="Show learning progress")

    # confidence
    p_conf = sub.add_parser("confidence", help="Check confidence about a topic")
    p_conf.add_argument("topic", help="Topic to check")

    # consolidate
    sub.add_parser("consolidate", help="Run consolidation cycle")

    # audit
    p_audit = sub.add_parser("audit", help="Show audit log")
    p_audit.add_argument("--last", type=int, help="Number of entries")

    # stats
    sub.add_parser("stats", help="Show store statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    curio = Curio()
    try:
        commands = {
            "observe": cmd_observe,
            "teach": cmd_teach,
            "gaps": cmd_gaps,
            "know": cmd_know,
            "progress": cmd_progress,
            "confidence": cmd_confidence,
            "consolidate": cmd_consolidate,
            "audit": cmd_audit,
            "stats": cmd_stats,
        }
        commands[args.command](args, curio)
    finally:
        curio.close()


if __name__ == "__main__":
    main()
