"""Curio — Baseline Comparisons.

Implements three baseline strategies to compare against Curio's learning approach:

1. PlainLLM    — No persistent memory; answers from parametric LLM knowledge only.
2. RAG         — Retrieves from a vector store at query time; no learning loop.
3. MemoryOnly  — Stores everything, never forgets; no consolidation or pruning.

Each baseline exposes the same query interface so the benchmark runner can
compare answer quality, confidence calibration, and memory efficiency against
Curio.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

@dataclass
class BaselineAnswer:
    """Uniform return type for all baselines."""
    answer: str
    confidence: float
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Lightweight cosine similarity (no numpy)."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a)) or 1e-10
    mag_b = math.sqrt(sum(x * x for x in b)) or 1e-10
    return dot / (mag_a * mag_b)


def _simple_hash_embedding(text: str, dim: int = 128) -> list[float]:
    """Deterministic hash-based pseudo-embedding (no ML dependency)."""
    import hashlib
    words = text.lower().split()
    vec = [0.0] * dim
    for i, word in enumerate(words):
        h = int(hashlib.sha256(word.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h // dim) % 2 == 0 else -1.0
        vec[idx] += sign * (1.0 / (1 + i))
    norm = math.sqrt(sum(x * x for x in vec)) or 1e-10
    return [x / norm for x in vec]


# ---------------------------------------------------------------------------
# 1. PlainLLM — No memory, no retrieval
# ---------------------------------------------------------------------------

class PlainLLM:
    """Baseline that answers purely from parametric knowledge.

    Strategy:
    - Stores nothing.
    - Cannot recall anything taught or observed.
    - Confidence is always 0 (no evidence base).
    - 'know' always returns empty.
    - 'gaps' always returns empty (cannot recognise what it doesn't know).
    """

    def __init__(self, data_dir: str | Path = "~/.curio/baselines/plain_llm"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._log: list[dict] = []

    # -- interface used by benchmark runner --

    def teach(self, content: str, domain: str = "", confidence: float = 0.8) -> None:
        self._log.append({"action": "teach", "content": content, "domain": domain})

    def observe(self, content: str, source: str = "", **kw) -> list:
        self._log.append({"action": "observe", "content": content, "source": source})
        return []  # no gaps detected — it has no knowledge to compare against

    def know(self, top_n: int = 10) -> list[dict[str, Any]]:
        return []  # remembers nothing

    def gaps(self) -> list[dict[str, Any]]:
        return []  # cannot identify unknowns

    def confidence(self, topic: str) -> float:
        return 0.0  # no evidence base

    def consolidate(self) -> dict:
        return {"pruned": 0, "compressed": 0}

    def progress(self) -> dict[str, Any]:
        return {"summary": {"active_knowledge": 0}}

    def show_audit(self, last_n: int = 20) -> list[dict]:
        return self._log[-last_n:]

    def answer(self, question: str) -> BaselineAnswer:
        return BaselineAnswer(
            answer=f"[PlainLLM] I have no specific knowledge about: {question}",
            confidence=0.0,
            sources=[],
            metadata={"memory_items": 0},
        )

    def close(self) -> None:
        pass


# ---------------------------------------------------------------------------
# 2. RAG — Retrieval-Augmented Generation (no learning loop)
# ---------------------------------------------------------------------------

class RAG:
    """Baseline that stores observations in a vector index and retrieves at query time.

    Strategy:
    - Stores every observation with a pseudo-embedding.
    - At query time, retrieves the top-k most similar stored items.
    - Confidence is proportional to retrieval similarity.
    - Does NOT detect gaps, contradictions, or staleness.
    - Does NOT consolidate or forget.
    """

    def __init__(self, data_dir: str | Path = "~/.curio/baselines/rag",
                 top_k: int = 5, sim_threshold: float = 0.3):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.top_k = top_k
        self.sim_threshold = sim_threshold
        self._index: list[dict[str, Any]] = []  # {content, embedding, source, domain}
        self._log: list[dict] = []

    def _index_item(self, content: str, source: str = "", domain: str = "") -> None:
        emb = _simple_hash_embedding(content)
        self._index.append({
            "content": content,
            "embedding": emb,
            "source": source,
            "domain": domain,
        })

    # -- interface used by benchmark runner --

    def teach(self, content: str, domain: str = "", confidence: float = 0.8) -> None:
        self._index_item(content, source="direct_teach", domain=domain)
        self._log.append({"action": "teach", "content": content})

    def observe(self, content: str, source: str = "", **kw) -> list:
        self._index_item(content, source=source)
        self._log.append({"action": "observe", "content": content, "source": source})
        return []  # RAG doesn't detect gaps

    def know(self, top_n: int = 10) -> list[dict[str, Any]]:
        return [
            {"content": item["content"], "source": item["source"]}
            for item in self._index[:top_n]
        ]

    def gaps(self) -> list[dict[str, Any]]:
        return []  # RAG has no gap detection

    def confidence(self, topic: str) -> float:
        if not self._index:
            return 0.0
        q_emb = _simple_hash_embedding(topic)
        best = max(_cosine_similarity(q_emb, item["embedding"]) for item in self._index)
        return max(0.0, min(1.0, best))

    def consolidate(self) -> dict:
        return {"pruned": 0, "compressed": 0}

    def progress(self) -> dict[str, Any]:
        return {"summary": {"active_knowledge": len(self._index)}}

    def show_audit(self, last_n: int = 20) -> list[dict]:
        return self._log[-last_n:]

    def answer(self, question: str) -> BaselineAnswer:
        if not self._index:
            return BaselineAnswer(
                answer=f"[RAG] No relevant documents in store for: {question}",
                confidence=0.0,
                sources=[],
                metadata={"index_size": 0},
            )
        q_emb = _simple_hash_embedding(question)
        ranked = sorted(
            self._index,
            key=lambda it: _cosine_similarity(q_emb, it["embedding"]),
            reverse=True,
        )[: self.top_k]
        top_sim = _cosine_similarity(q_emb, ranked[0]["embedding"]) if ranked else 0.0
        if top_sim < self.sim_threshold:
            return BaselineAnswer(
                answer=f"[RAG] No sufficiently relevant results for: {question}",
                confidence=0.0,
                sources=[],
                metadata={"index_size": len(self._index)},
            )
        snippets = "\n".join(f"- {r['content']} (source: {r['source']})" for r in ranked)
        return BaselineAnswer(
            answer=f"[RAG] Retrieved {len(ranked)} relevant items:\n{snippets}",
            confidence=round(top_sim, 3),
            sources=[r["source"] for r in ranked],
            metadata={"index_size": len(self._index)},
        )

    def close(self) -> None:
        pass


# ---------------------------------------------------------------------------
# 3. MemoryOnly — Stores everything, never forgets
# ---------------------------------------------------------------------------

class MemoryOnly:
    """Baseline that accumulates all knowledge without any forgetting mechanism.

    Strategy:
    - Stores every teach and observe with timestamps.
    - Later entries override earlier ones for the same topic (last-writer-wins).
    - No consolidation, no pruning, no decay.
    - Confidence is based on recency and frequency of mentions.
    - Contradictions are kept as-is (no resolution).
    """

    def __init__(self, data_dir: str | Path = "~/.curio/baselines/memory_only"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._memory: list[dict[str, Any]] = []
        self._topic_mentions: dict[str, int] = {}
        self._log: list[dict] = []

    def _record(self, content: str, source: str = "", domain: str = "") -> None:
        import time
        self._memory.append({
            "content": content,
            "source": source,
            "domain": domain,
            "timestamp": time.time(),
            "index": len(self._memory),
        })
        # track topic mention counts
        for word in content.lower().split():
            if len(word) > 4:  # skip tiny words
                self._topic_mentions[word] = self._topic_mentions.get(word, 0) + 1

    # -- interface used by benchmark runner --

    def teach(self, content: str, domain: str = "", confidence: float = 0.8) -> None:
        self._record(content, source="direct_teach", domain=domain)
        self._log.append({"action": "teach", "content": content})

    def observe(self, content: str, source: str = "", **kw) -> list:
        self._record(content, source=source)
        self._log.append({"action": "observe", "content": content, "source": source})
        return []  # MemoryOnly never detects gaps or contradictions

    def know(self, top_n: int = 10) -> list[dict[str, Any]]:
        # Returns all items sorted by recency
        sorted_mem = sorted(self._memory, key=lambda m: m["index"], reverse=True)
        return [
            {"content": m["content"], "source": m["source"]}
            for m in sorted_mem[:top_n]
        ]

    def gaps(self) -> list[dict[str, Any]]:
        return []  # never identifies gaps

    def confidence(self, topic: str) -> float:
        if not self._memory:
            return 0.0
        # Score based on mention frequency + recency
        topic_lower = topic.lower()
        words = topic_lower.split()
        total_mentions = sum(self._topic_mentions.get(w, 0) for w in words)
        total_words = sum(self._topic_mentions.values()) or 1
        frequency_score = min(1.0, total_mentions / (total_words * 0.3 + 1))

        # Recency boost: how close to the latest entry
        import time
        now = time.time()
        latest = max(m["timestamp"] for m in self._memory)
        recency_score = 1.0 / (1.0 + (now - latest) / 3600)

        return round(min(1.0, (frequency_score * 0.6 + recency_score * 0.4)), 3)

    def consolidate(self) -> dict:
        # MemoryOnly never consolidates — stores everything
        return {"pruned": 0, "compressed": 0}

    def progress(self) -> dict[str, Any]:
        return {"summary": {"active_knowledge": len(self._memory)}}

    def show_audit(self, last_n: int = 20) -> list[dict]:
        return self._log[-last_n:]

    def answer(self, question: str) -> BaselineAnswer:
        if not self._memory:
            return BaselineAnswer(
                answer=f"[MemoryOnly] No memory stored for: {question}",
                confidence=0.0,
                sources=[],
                metadata={"memory_size": 0},
            )
        # Simple keyword match to find relevant memories
        q_words = set(question.lower().split())
        scored = []
        for item in self._memory:
            item_words = set(item["content"].lower().split())
            overlap = len(q_words & item_words)
            scored.append((overlap, item))
        scored.sort(key=lambda x: (-x[0], -x[1]["index"]))

        relevant = [(s, m) for s, m in scored if s > 0][:5]
        if not relevant:
            return BaselineAnswer(
                answer=f"[MemoryOnly] No matching memories for: {question} (have {len(self._memory)} items)",
                confidence=0.0,
                sources=[],
                metadata={"memory_size": len(self._memory)},
            )
        snippets = "\n".join(
            f"- {m['content']} (source: {m['source']})" for _, m in relevant
        )
        conf = min(1.0, relevant[0][0] / max(len(q_words), 1))
        return BaselineAnswer(
            answer=f"[MemoryOnly] Found {len(relevant)} relevant memories:\n{snippets}",
            confidence=round(conf, 3),
            sources=[m["source"] for _, m in relevant],
            metadata={"memory_size": len(self._memory)},
        )

    def close(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Baseline registry
# ---------------------------------------------------------------------------

BASELINES: dict[str, type] = {
    "PlainLLM": PlainLLM,
    "RAG": RAG,
    "MemoryOnly": MemoryOnly,
}


def get_baseline(name: str, **kwargs) -> Any:
    """Instantiate a baseline by name."""
    if name not in BASELINES:
        raise ValueError(f"Unknown baseline: {name}. Choose from: {list(BASELINES.keys())}")
    return BASELINES[name](**kwargs)


def run_all_baselines(benchmark_tasks: list[dict],
                      data_dir: str | Path = "~/.curio/baselines") -> dict[str, list[dict]]:
    """Run all baselines against benchmark tasks and return per-baseline results.

    Returns a dict mapping baseline name -> list of per-task result dicts.
    Each result dict has: id, name, type, passed, errors, answer (BaselineAnswer).
    """
    results: dict[str, list[dict]] = {}
    for name in BASELINES:
        baseline_results = []
        for task in benchmark_tasks:
            baseline = get_baseline(name, data_dir=str(Path(data_dir) / name.lower()))
            task_result = {
                "id": task["id"],
                "name": task["name"],
                "type": task["type"],
                "passed": True,
                "errors": [],
                "answer": None,
            }
            try:
                for step in task["steps"]:
                    action = step["action"]
                    if action == "teach":
                        baseline.teach(
                            content=step["content"],
                            domain=step.get("domain", ""),
                            confidence=step.get("confidence", 0.8),
                        )
                    elif action == "observe":
                        gaps = baseline.observe(
                            content=step["content"],
                            source=step.get("source", ""),
                        )
                        if "expected_min_gaps" in step:
                            if len(gaps) < step["expected_min_gaps"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected >= {step['expected_min_gaps']} gaps, got {len(gaps)}"
                                )
                        if "expected_gap_type" in step:
                            found = any(g.get("type") == step["expected_gap_type"] for g in gaps)
                            if not found:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected gap type {step['expected_gap_type']}, not found"
                                )
                    elif action == "know":
                        known = baseline.know()
                        if "expected_min_items" in step:
                            if len(known) < step["expected_min_items"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected >= {step['expected_min_items']} items, got {len(known)}"
                                )
                        if "expected_content_contains" in step:
                            all_content = " ".join(k.get("content", "") for k in known)
                            for term in step["expected_content_contains"]:
                                if term.lower() not in all_content.lower():
                                    task_result["passed"] = False
                                    task_result["errors"].append(
                                        f"Expected '{term}' in knowledge, not found"
                                    )
                    elif action == "confidence":
                        score = baseline.confidence(step["topic"])
                        if "expected_min" in step:
                            if score < step["expected_min"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected confidence >= {step['expected_min']} "
                                    f"for '{step['topic']}', got {score:.3f}"
                                )
                        if "expected_max" in step:
                            if score > step["expected_max"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected confidence <= {step['expected_max']} "
                                    f"for '{step['topic']}', got {score:.3f}"
                                )
                    elif action == "gaps":
                        gaps = baseline.gaps()
                        if "expected_min_gaps" in step:
                            if len(gaps) < step["expected_min_gaps"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected >= {step['expected_min_gaps']} open gaps, got {len(gaps)}"
                                )
                    elif action == "know_or_gaps":
                        known = baseline.know()
                        gaps = baseline.gaps()
                        either_ok = False
                        if "expected_either_knowledge_min" in step:
                            if len(known) >= step["expected_either_knowledge_min"]:
                                either_ok = True
                        if "expected_either_gaps_min" in step:
                            if len(gaps) >= step["expected_either_gaps_min"]:
                                either_ok = True
                        if not either_ok:
                            task_result["passed"] = False
                            task_result["errors"].append(
                                f"Expected either >= {step.get('expected_either_knowledge_min', 0)} "
                                f"knowledge or >= {step.get('expected_either_gaps_min', 0)} gaps. "
                                f"Got {len(known)} knowledge, {len(gaps)} gaps"
                            )
                    elif action == "consolidate":
                        baseline.consolidate()
                    elif action == "progress":
                        progress = baseline.progress()
                        if "expected_min_knowledge" in step:
                            if progress["summary"]["active_knowledge"] < step["expected_min_knowledge"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected >= {step['expected_min_knowledge']} knowledge, "
                                    f"got {progress['summary']['active_knowledge']}"
                                )
                    elif action == "audit":
                        entries = baseline.show_audit()
                        if "expected_min_entries" in step:
                            if len(entries) < step["expected_min_entries"]:
                                task_result["passed"] = False
                                task_result["errors"].append(
                                    f"Expected >= {step['expected_min_entries']} audit entries, "
                                    f"got {len(entries)}"
                                )
            except Exception as e:
                task_result["passed"] = False
                task_result["errors"].append(f"Exception: {type(e).__name__}: {e}")
            finally:
                baseline.close()
            baseline_results.append(task_result)
        results[name] = baseline_results
    return results


def compare_results(curio_results: dict, baseline_results: dict[str, list[dict]]) -> dict:
    """Compare Curio results against each baseline.

    Returns a summary dict with per-baseline pass rates and a head-to-head table.
    """
    curio_pass = sum(1 for r in curio_results.get("results", []) if r.get("passed"))
    curio_total = curio_results.get("total", 0)

    comparison = {
        "curio": {
            "passed": curio_pass,
            "total": curio_total,
            "pass_rate": round(curio_pass / curio_total * 100, 1) if curio_total else 0,
        },
        "baselines": {},
        "advantages": [],
    }

    for name, results in baseline_results.items():
        b_pass = sum(1 for r in results if r.get("passed"))
        b_total = len(results)
        b_rate = round(b_pass / b_total * 100, 1) if b_total else 0
        curio_adv = curio_pass - b_pass
        comparison["baselines"][name] = {
            "passed": b_pass,
            "total": b_total,
            "pass_rate": b_rate,
        }
        comparison["advantages"].append({
            "baseline": name,
            "curio_advantage": curio_adv,
            "curio_advantage_pct": round(
                (comparison["curio"]["pass_rate"] - b_rate), 1
            ),
        })

    return comparison


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    tasks_file = Path(__file__).parent / "benchmark_tasks.json"
    if len(sys.argv) > 1:
        tasks_file = Path(sys.argv[1])

    with open(tasks_file) as f:
        tasks = json.load(f)

    print(f"Running {len(tasks)} benchmark tasks across {len(BASELINES)} baselines...\n")

    results = run_all_baselines(tasks)

    for name, task_results in results.items():
        passed = sum(1 for r in task_results if r["passed"])
        total = len(task_results)
        print(f"{'=' * 50}")
        print(f"Baseline: {name}")
        print(f"  Passed: {passed}/{total} ({passed / total * 100:.1f}%)" if total else "  No tasks")
        for r in task_results:
            status = "✅" if r["passed"] else "❌"
            print(f"  {status} {r['id']}: {r['name']}")
            if r["errors"]:
                for err in r["errors"]:
                    print(f"      Error: {err}")
        print()
