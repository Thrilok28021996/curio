# Curio — Findings and Decisions

## Product thesis
Quality of learned knowledge matters more than the amount of stored data. Curio should learn selectively, maintain confidence and provenance, and forget what no longer helps.

## Prior-art findings
- Mem0 and similar systems primarily provide memory storage and retrieval.
- Hindsight, LangMem, TencentDB Agent Memory, and related systems implement partial learning or skill extraction.
- Cognee and CrewAI provide parts of memory consolidation and forgetting.
- Nemori provides prediction-based gap detection from conversational experience.
- ALAS and U-Mem are close research systems for curriculum/gap-driven acquisition, but lack a complete selective-forgetting and progress-tracking loop.
- The full six-part loop has not been found in one mature product.

## Important constraints
- Broko belongs to the employer. It cannot be used as Curio's codebase, dataset, domain corpus, customer proof, or product foundation.
- Curio needs an independent domain and independently collected data.
- Autonomous learning must remain auditable, reversible, and bounded.

## Unresolved decisions
- First target: personal learning assistant vs developer learning agent.
- Local-first vs hybrid deployment.
- Whether to expose Curio as an application, SDK, or both.
- Exact definition of “learning progress” for the first benchmark.
