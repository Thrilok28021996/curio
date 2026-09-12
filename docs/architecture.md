# Curio — Architecture

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    CURIO LEARNING AGENT                      │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ PERCEIVE │  │ COMPARE  │  │  DETECT  │  │ APPRAISE │   │
│  │          │→ │          │→ │   GAP    │→ │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                       │     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────▼──┐   │
│  │VALIDATE  │← │CONSOLI-  │← │  LEARN   │← │   SEEK   │   │
│  │          │  │  DATE    │  │          │  │          │   │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────┘   │
│       │                                                     │
│       └────── Loop back to PERCEIVE ──────────────────────  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              KNOWLEDGE LAYER                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Knowledge│  │ Source   │  │ Audit    │           │   │
│  │  │ Graph    │  │ Trust DB │  │ Log      │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              METACOGNITION LAYER                      │   │
│  │  ┌──────────┐  ┌──────────┐                           │   │
│  │  │ Domain   │  │ Learning │                           │   │
│  │  │ Map      │  │ Progress │                           │   │
│  │  └──────────┘  └──────────┘                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Map

| Component | File | Purpose |
|---|---|---|
| `Perceiver` | `src/perceiver.py` | Ingests raw observations, normalizes them |
| `Comparator` | `src/comparator.py` | Compares observations against knowledge graph |
| `GapDetector` | `src/gap_detector.py` | Identifies knowledge gaps from comparisons |
| `RelevanceFilter` | `src/relevance_filter.py` | Scores gaps, decides LEARN/DEFER/IGNORE |
| `KnowledgeSeeker` | `src/knowledge_seeker.py` | Searches and retrieves information |
| `KnowledgeIntegrator` | `src/knowledge_integrator.py` | Processes, validates, and stores lessons |
| `MemoryConsolidator` | `src/memory_consolidator.py` | Decays, compresses, prunes, reinforces |
| `KnowledgeMap` | `src/knowledge_map.py` | Tracks domain coverage and confidence |
| `AuditLog` | `src/audit_log.py` | Records every learning decision |

## Data Flow

```text
Observation
    → Perceiver (normalize)
    → Comparator (match against KG)
    → GapDetector (identify gaps)
    → RelevanceFilter (score and decide)
    → KnowledgeSeeker (find information)
    → KnowledgeIntegrator (extract lesson, store)
    → MemoryConsolidator (periodic maintenance)
    → KnowledgeMap (update coverage)
    → AuditLog (record everything)
```

## Storage

| Store | Technology | Purpose |
|---|---|---|
| Knowledge graph | Qdrant (vectors) + NetworkX (graph) | Store and retrieve knowledge nodes |
| Source trust DB | SQLite | Track source reliability over time |
| Audit log | JSONL file | Every learning decision with timestamp |
| Domain map | JSON / SQLite | Coverage and confidence per domain |

## Evaluation

| Component | File | Purpose |
|---|---|---|
| Benchmark tasks | `eval/benchmark_tasks.json` | Test cases with known answers |
| Baselines | `eval/baselines/` | Plain LLM, RAG, memory-only |
| Results | `eval/results/` | Evaluation outputs and comparisons |
| Tests | `tests/` | Unit tests for each component |
