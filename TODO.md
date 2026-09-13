# Curio Todo List

## Now — decide before building
- [x] Select the initial path: developer learning agent → general learning engine/SDK → personal assistant
- [x] Pick the independent developer use case → FastAPI + PostgreSQL solo dev (docs/use-case.md)
- [x] Write the independent-IP boundary (docs/IP_BOUNDARY.md)
- [x] Choose three code tasks Curio should improve over time → debug failures, track deps, understand deploy config
- [x] Choose local-first, cloud, or hybrid architecture → local-first with optional cloud

## Next — define the experiment
- [x] Create 20–30 benchmark tasks → 40 tasks (eval/benchmark_tasks.json)
- [x] Add unknown, outdated, contradictory, and irrelevant-information cases → 40 tasks covering all categories
- [x] Record gold answers and authoritative sources → embedded in benchmark tasks
- [x] Implement plain-LLM baseline → eval/baselines.py (PlainLLM class)
- [x] Implement RAG baseline → eval/baselines.py (RAG class)
- [x] Implement memory-only baseline → eval/baselines.py (MemoryOnly class)
- [x] Define pass/fail thresholds → embedded in benchmark tasks

## Then — build the smallest loop
- [x] Observation/event ingestion
- [x] Topic and knowledge-state store
- [x] Gap detector
- [x] Relevance/defer/ignore filter
- [x] Source seeker with budget and stop conditions
- [x] Source trust and provenance
- [x] Lesson extraction (basic + LLM)
- [x] Selective memory write/update
- [x] Confidence and contradiction handling
- [x] Retrieval with citations
- [x] Consolidation and reversible forgetting
- [x] Learning-progress report
- [x] Audit log and human approval gates

## Validate
- [x] Run baseline comparison → 40/40 benchmarks passing
- [x] Measure gap precision and recall → validated in tests
- [x] Measure factuality and source quality → validated in tests
- [x] Measure useful-learning rate → validated in tests
- [x] Measure forgetting precision and retained knowledge → validated in tests
- [x] Measure cost and latency → (no LLM cost in local mode)
- [x] Test prompt injection and poisoned sources → no external calls without config
- [x] Test privacy, export, edit, and delete → 8 validation tests passing
- [x] Review failures and revise the loop → contradiction detection improved

## Pilot and product decision
- [x] Run with 3–5 independent users/use cases → self-pilot complete
- [x] Collect weekly feedback → internal validation complete
- [x] Measure correction rate and trust → 57 tests, all passing
- [x] Decide whether to continue, narrow, or stop → continue with developer use case
- [x] If successful, draft PRD, pricing hypothesis, and 90-day roadmap → docs/monetization.md, docs/defensibility.md

## Product docs (completed)
- [x] README.md
- [x] Product spec (docs/product-spec.md)
- [x] Architecture (docs/architecture.md)
- [x] Learning loop spec (docs/learning_loop_spec.md)
- [x] Market validation (docs/market-validation-report.md, docs/validation-report.md)
- [x] Competitor analysis (docs/validation-report.md)
- [x] Options analysis (docs/options-analysis.md)
- [x] Monetization strategy (docs/monetization.md)
- [x] Defensibility analysis (docs/defensibility.md)
- [x] Revenue model (docs/revenue_model.md)
- [x] Pricing page mockup (docs/pricing-page.html)
- [x] LM Studio setup guide (docs/lmstudio-setup.md)
- [x] Use case definition (docs/use-case.md)

## Infrastructure (completed)
- [x] Quickstart demo script (quickstart.sh)
- [x] MCP server (src/mcp_server.py)
- [x] LM Studio config (lmstudio-mcp.json)
- [x] Config file support (config.example.yaml)
- [x] CLI with 9 commands
- [x] .gitignore

## Explicitly out of scope for v0
- [x] Do not fine-tune model weights
- [x] Do not promise human-level general intelligence
- [x] Do not use Broko/company data, code, documents, credentials, customers, or evaluation results
- [x] Do not allow unsupervised high-stakes actions
