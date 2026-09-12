# Curio Todo List

## Now — decide before building
- [x] Select the initial path: developer learning agent → general learning engine/SDK → personal assistant
- [ ] Pick the independent developer use case and target user
- [ ] Write the independent-IP boundary
- [ ] Choose three code tasks Curio must improve over time
- [ ] Choose local-first, cloud, or hybrid architecture

## Next — define the experiment
- [ ] Create 20–30 benchmark tasks
- [ ] Add unknown, outdated, contradictory, and irrelevant-information cases
- [ ] Record gold answers and authoritative sources
- [ ] Implement plain-LLM baseline
- [ ] Implement RAG baseline
- [ ] Implement memory-only baseline
- [ ] Define pass/fail thresholds

## Then — build the smallest loop
- [x] Observation/event ingestion
- [x] Topic and knowledge-state store
- [x] Gap detector
- [x] Relevance/defer/ignore filter
- [x] Source seeker with budget and stop conditions
- [x] Source trust and provenance
- [x] Lesson extraction
- [x] Selective memory write/update
- [ ] Confidence and contradiction handling (basic)
- [x] Retrieval with citations
- [x] Consolidation and reversible forgetting
- [x] Learning-progress report
- [x] Audit log and human approval gates

## Validate
- [ ] Run baseline comparison
- [ ] Measure gap precision and recall
- [ ] Measure factuality and source quality
- [ ] Measure useful-learning rate
- [ ] Measure forgetting precision and retained knowledge
- [ ] Measure cost and latency
- [ ] Test prompt injection and poisoned sources
- [ ] Test privacy, export, edit, and delete
- [ ] Review failures and revise the loop

## Pilot and product decision
- [ ] Run with 3–5 independent users/use cases
- [ ] Collect weekly feedback
- [ ] Measure correction rate and trust
- [ ] Decide whether to continue, narrow, or stop
- [ ] If successful, draft PRD, pricing hypothesis, and 90-day roadmap

## Explicitly out of scope for v0
- [ ] Do not fine-tune model weights
- [ ] Do not promise human-level general intelligence
- [ ] Do not use Broko/company data, code, documents, credentials, customers, or evaluation results
- [ ] Do not allow unsupervised high-stakes actions
