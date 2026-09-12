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
- [ ] Choose the first independent use case
- [ ] Define evaluation benchmark
- [ ] Build a narrow research prototype
- [ ] Run controlled experiments
- [ ] Decide whether to productize

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
Status: in_progress
- [ ] Confirm the independent domain and target user
- [ ] Create an IP boundary document excluding Broko/company assets
- [ ] Define allowed data sources and privacy rules
- [ ] Define what Curio may do autonomously and what requires approval
- [ ] Select the first 3 user jobs-to-be-done

### Phase 1 — Learning-loop specification
Status: pending
- [ ] Specify gap types: unknown, incomplete, outdated, contradictory
- [ ] Specify relevance scoring and defer/ignore behavior
- [ ] Specify source trust, provenance, and conflict handling
- [ ] Specify lesson schema and knowledge graph relationships
- [ ] Specify consolidation, decay, archive, deletion, and recovery rules
- [ ] Specify progress and mastery metrics
- [ ] Define threat model: hallucinated learning, prompt injection, poisoned sources, privacy leakage

### Phase 2 — Evaluation before implementation
Status: pending
- [ ] Create a small task set with known answers and deliberate knowledge gaps
- [ ] Create scenarios for outdated and contradictory information
- [ ] Define baseline systems: plain LLM, RAG, memory-only agent
- [ ] Define metrics: gap precision/recall, learning usefulness, factuality, source quality, retention, forgetting precision, cost, latency
- [ ] Define pass/fail thresholds
- [ ] Create an evaluation log format with reproducible seeds and model versions

### Phase 3 — Research prototype
Status: pending
- [ ] Implement event and observation ingestion
- [ ] Implement knowledge state and topic map
- [ ] Implement gap detector
- [ ] Implement relevance filter
- [ ] Implement source-seeking worker
- [ ] Implement source verification and provenance
- [ ] Implement lesson extraction and selective storage
- [ ] Implement retrieval with confidence and citations
- [ ] Implement consolidation and reversible forgetting
- [ ] Implement progress dashboard/report
- [ ] Add approval gates for risky learning/actions

### Phase 4 — Controlled experiments
Status: pending
- [ ] Run baseline comparison
- [ ] Test autonomous gap detection
- [ ] Test source disagreement and correction
- [ ] Test stale knowledge replacement
- [ ] Test noise and irrelevant information resistance
- [ ] Test memory growth and cost over time
- [ ] Test whether forgetting improves answers rather than merely reducing storage
- [ ] Review every failure and classify the root cause

### Phase 5 — Private pilot
Status: pending
- [ ] Recruit 3–5 independent users or use cases
- [ ] Add consent, export, edit, delete, and audit controls
- [ ] Monitor false learning and unwanted autonomous actions
- [ ] Measure weekly retention, useful recalls, corrections, and user trust
- [ ] Collect structured feedback
- [ ] Decide whether the system creates repeatable value

### Phase 6 — Product decision
Status: pending
- [ ] Decide product category: personal assistant, developer tool, or learning API
- [ ] Define the narrowest buyer and pricing hypothesis
- [ ] Decide local-first, cloud, or hybrid deployment
- [ ] Decide open-source boundary
- [ ] Write a product requirements document
- [ ] Create a 90-day build roadmap only if pilot evidence passes thresholds

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
