"""Curio — Benchmark Runner.

Executes benchmark tasks and reports results.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.curio import Curio


def run_benchmark(tasks_path: str = "eval/benchmark_tasks.json") -> dict:
    """Run all benchmark tasks and return results."""
    tasks_file = Path(__file__).parent.parent / tasks_path
    with open(tasks_file) as f:
        tasks = json.load(f)

    results = []
    passed = 0
    failed = 0

    for task in tasks:
        result = run_task(task)
        results.append(result)
        if result["passed"]:
            passed += 1
        else:
            failed += 1

    summary = {
        "total": len(tasks),
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed / len(tasks) * 100:.1f}%",
        "results": results,
    }

    return summary


def run_task(task: dict) -> dict:
    """Run a single benchmark task."""
    tmp = tempfile.mkdtemp()
    curio = Curio(data_dir=Path(tmp))

    result = {
        "id": task["id"],
        "name": task["name"],
        "type": task["type"],
        "passed": True,
        "errors": [],
    }

    try:
        for step in task["steps"]:
            action = step["action"]

            if action == "teach":
                curio.teach(
                    content=step["content"],
                    domain=step.get("domain", ""),
                    confidence=step.get("confidence", 0.8),
                )

            elif action == "observe":
                gaps = curio.observe(
                    content=step["content"],
                    source=step.get("source", ""),
                )
                if "expected_min_gaps" in step:
                    if len(gaps) < step["expected_min_gaps"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected >= {step['expected_min_gaps']} gaps, got {len(gaps)}"
                        )
                if "expected_gap_type" in step:
                    found = any(g.type.value == step["expected_gap_type"] for g in gaps)
                    if not found:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected gap type {step['expected_gap_type']}, not found"
                        )

            elif action == "know":
                known = curio.know()
                if "expected_min_items" in step:
                    if len(known) < step["expected_min_items"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected >= {step['expected_min_items']} items, got {len(known)}"
                        )
                if "expected_content_contains" in step:
                    all_content = " ".join(k["content"] for k in known)
                    for term in step["expected_content_contains"]:
                        if term.lower() not in all_content.lower():
                            result["passed"] = False
                            result["errors"].append(
                                f"Expected '{term}' in knowledge, not found"
                            )

            elif action == "confidence":
                score = curio.confidence(step["topic"])
                if "expected_min" in step:
                    if score < step["expected_min"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected confidence >= {step['expected_min']} for '{step['topic']}', got {score:.3f}"
                        )
                if "expected_max" in step:
                    if score > step["expected_max"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected confidence <= {step['expected_max']} for '{step['topic']}', got {score:.3f}"
                        )

            elif action == "gaps":
                gaps = curio.gaps()
                if "expected_min_gaps" in step:
                    if len(gaps) < step["expected_min_gaps"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected >= {step['expected_min_gaps']} open gaps, got {len(gaps)}"
                        )

            elif action == "know_or_gaps":
                # Either knowledge was learned OR gaps were detected
                known = curio.know()
                gaps = curio.gaps()
                either_ok = False
                if "expected_either_knowledge_min" in step:
                    if len(known) >= step["expected_either_knowledge_min"]:
                        either_ok = True
                if "expected_either_gaps_min" in step:
                    if len(gaps) >= step["expected_either_gaps_min"]:
                        either_ok = True
                if not either_ok:
                    result["passed"] = False
                    result["errors"].append(
                        f"Expected either >= {step.get('expected_either_knowledge_min', 0)} knowledge "
                        f"or >= {step.get('expected_either_gaps_min', 0)} gaps. "
                        f"Got {len(known)} knowledge, {len(gaps)} gaps"
                    )

            elif action == "consolidate":
                curio.consolidate()

            elif action == "progress":
                progress = curio.progress()
                if "expected_min_knowledge" in step:
                    if progress["summary"]["active_knowledge"] < step["expected_min_knowledge"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected >= {step['expected_min_knowledge']} knowledge, "
                            f"got {progress['summary']['active_knowledge']}"
                        )

            elif action == "audit":
                entries = curio.show_audit()
                if "expected_min_entries" in step:
                    if len(entries) < step["expected_min_entries"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"Expected >= {step['expected_min_entries']} audit entries, got {len(entries)}"
                        )

    except Exception as e:
        result["passed"] = False
        result["errors"].append(f"Exception: {type(e).__name__}: {e}")

    finally:
        curio.close()

    return result


def main():
    """Run benchmarks and print results."""
    print("Running Curio benchmarks...\n")
    summary = run_benchmark()

    for r in summary["results"]:
        status = "✅" if r["passed"] else "❌"
        print(f"  {status} {r['id']}: {r['name']}")
        if r["errors"]:
            for err in r["errors"]:
                print(f"      Error: {err}")

    print(f"\n{'=' * 50}")
    print(f"Results: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']})")

    if summary["failed"] > 0:
        print(f"\n{summary['failed']} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll benchmarks passed!")


if __name__ == "__main__":
    main()
