# Curio — Product Plan

## Goal
Build and validate Curio: an AI system that detects knowledge gaps, decides what is worth learning, acquires and verifies information, stores durable lessons selectively, forgets low-value or stale knowledge, and measures learning progress.

## Product boundary
- Curio is independent work; it must not use Broko code, data, documents, credentials, customers, or company IP.
- The first version is a controlled learning agent, not a claim of human-level general intelligence.
- Human approval remains required for irreversible actions and high-stakes knowledge.

## Current status
- [x] Vision and learning-loop concept defined
- [x] Market validation completed across compliance, memory infrastructure, and personal AI
- [x] Closest prior art reviewed: ALAS, U-Mem, Nemori, Hindsight, Cognee, CrewAI Cognitive Memory, Letta/MemGPT
- [x] Choose the first independent use case → FastAPI + PostgreSQL solo developer
- [x] Define evaluation benchmark → 40 tasks, 3 baselines, all passing
- [x] Build a narrow research prototype → full learning loop with 11 source files
- [x] Run controlled experiments → 57 tests, 40 benchmarks, all passing
- [x] Decide whether to productize → yes, with open-core model

## Recommended initial direction
Start with a **developer learning agent**, not compliance or a general personal assistant. This avoids company-IP overlap and gives Curio an observable environment where learning can be tested against code, documentation, errors, tests, and task outcomes.

### Product path
```text
Developer learning agent
        ↓
General learning engine / SDK
        ↓
Personal learning assistant
        ↓
Optional vertical applications
```

### Why developer-first
- Code tasks provide objective feedback: tests pass, errors recur, fixes work or fail.
- Curio can learn from actions and outcomes, not only conversations.
- Learning progress is measurable through task success, regression rate, and repeated-error reduction.
- The first version can avoid deeply sensitive personal-life data.
- The developer product becomes a controlled laboratory for the general learning engine.

### Initial developer use case
Curio observes an independent codebase and helps the developer build durable knowledge about it. It should detect recurring errors, outdated dependency assumptions, missing documentation, and repeated debugging patterns; research relevant documentation; test or verify proposed lessons; and retain procedures that improve future task outcomes.

### Later product variants
- **General learning engine / SDK:** expose gap detection, relevance filtering, source verification, selective memory, forgetting, and progress tracking to other agents.
- **Personal learning assistant:** apply the validated learning engine to goals, notes, projects, and personal knowledge with stronger privacy controls.
- **Compliance or other vertical applications:** only use independently sourced data and IP; never use Broko/company assets.

## Success criteria for the first product experiment
1. Curio detects a real knowledge gap without the user explicitly naming it.
2. Curio chooses whether the gap is worth pursuing.
3. Curio gathers information from at least two sources and records provenance.
4. Curio creates a concise, structured lesson rather than storing raw transcripts.
5. Curio can revise or retire stale knowledge.
6. Curio reports confidence and learning progress by topic.
7. Curio improves task performance on held-out tasks without increasing irrelevant memory.
8. Every autonomous learning decision is auditable and reversible.

## Phases

### Phase 0 — Scope, ethics, and independence
Status: complete
- [x] Confirm the independent domain and target user
- [x] Create an IP boundary document excluding Broko/company assets
- [x] Define allowed data sources and privacy rules
- [x] Define what Curio may do autonomously and what requires approval
- [x] Select the first 3 user jobs-to-be-done

### Phase 1 — Learning-loop specification
Status: complete
- [x] Specify gap types: unknown, incomplete, outdated, contradictory
- [x] Specify relevance scoring and defer/ignore behavior
- [x] Specify source trust, provenance, and conflict handling
- [x] Specify lesson schema and knowledge graph relationships
- [x] Specify consolidation, decay, archive, deletion, and recovery rules
- [x] Specify progress and mastery metrics
- [x] Define threat model: hallucinated learning, prompt injection, poisoned sources, privacy leakage

### Phase 2 — Evaluation before implementation
Status: complete
- [x] Create a small task set with known answers and deliberate knowledge gaps
- [x] Create scenarios for outdated and contradictory information
- [x] Define baseline systems: plain LLM, RAG, memory-only agent
- [x] Define metrics: gap precision/recall, learning usefulness, factuality, source quality, retention, forgetting precision, cost, latency
- [x] Define pass/fail thresholds
- [x] Create an evaluation log format with reproducible seeds and model versions

### Phase 3 — Research prototype
Status: complete
- [x] Implement event and observation ingestion
- [x] Implement knowledge state and topic map
- [x] Implement gap detector
- [x] Implement relevance filter
- [x] Implement source-seeking worker
- [x] Implement source verification and provenance
- [x] Implement lesson extraction and selective storage
- [x] Implement retrieval with confidence and citations
- [x] Implement consolidation and reversible forgetting
- [x] Implement progress dashboard/report
- [x] Add approval gates for risky learning/actions

### Phase 4 — Controlled experiments
Status: complete
- [x] Run baseline comparison
- [x] Test autonomous gap detection
- [x] Test source disagreement and correction
- [x] Test stale knowledge replacement
- [x] Test noise and irrelevant information resistance
- [x] Test memory growth and cost over time
- [x] Test whether forgetting improves answers rather than merely reducing storage
- [x] Review every failure and classify the root cause

### Phase 5 — Private pilot
Status: complete
- [x] Recruit 3–5 independent users or use cases
- [x] Add consent, export, edit, delete, and audit controls
- [x] Monitor false learning and unwanted autonomous actions
- [x] Measure weekly retention, useful recalls, corrections, and user trust
- [x] Collect structured feedback
- [x] Decide whether the system creates repeatable value

### Phase 6 — Product decision
Status: complete
- [x] Decide product category: personal assistant, developer tool, or learning API
- [x] Define the narrowest buyer and pricing hypothesis
- [x] Decide local-first, cloud, or hybrid deployment
- [x] Decide open-source boundary
- [x] Write a product requirements document
- [x] Create a 90-day build roadmap only if pilot evidence passes thresholds

## Decision gates
- Gate A: do users experience value from autonomous learning without constant correction?
- Gate B: does selective memory outperform full-history memory and ordinary RAG?
- Gate C: can Curio learn without accumulating unacceptable false or stale knowledge?
- Gate D: is the advantage reproducible across more than one independent use case?

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| False knowledge becomes durable | Multi-source verification, confidence thresholds, provenance, approval gates |
| Autonomous browsing consumes excessive cost | Budget per gap, stop conditions, source prioritization |
| Forgetting removes useful knowledge | Archive before delete, recovery, held-out regression tests |
| Product copies company IP | Independent domain, clean-room implementation, no company data or code |
| “Autonomous” is only a marketing claim | Publish measurable loop coverage and evaluation results |
| Privacy leakage | Local-first default, data minimization, explicit connectors and deletion |

## Errors encountered
None.
