# Curio — Learning Loop Specification

## Overview
Curio implements an 8-step autonomous learning loop. Each step is a discrete component with clear inputs, outputs, and failure modes.

---

## Step 1: PERCEIVE
**Input:** Raw information (user query, file change, log entry, web content, conversation)
**Output:** Normalized observation record

```json
{
  "observation_id": "uuid",
  "type": "query|event|document|conversation|error|system",
  "content": "string",
  "source": "string",
  "timestamp": "ISO8601",
  "metadata": {}
}
```

---

## Step 2: COMPARE
**Input:** Observation + current knowledge graph
**Output:** Match score per knowledge node

- Embed the observation and compare against stored knowledge
- Find nearest neighbors in vector space
- Calculate semantic similarity
- Flag matches below threshold as potential gaps

---

## Step 3: DETECT GAP
**Input:** Comparison results
**Output:** Gap record

Gap types:
- `UNKNOWN` — no prior knowledge exists
- `INCOMPLETE` — partial knowledge, missing key details
- `OUTDATED` — knowledge exists but may be stale
- `CONTRADICTORY` — new info conflicts with stored knowledge

```json
{
  "gap_id": "uuid",
  "type": "UNKNOWN|INCOMPLETE|OUTDATED|CONTRADICTORY",
  "topic": "string",
  "confidence": 0.0-1.0,
  "priority": "HIGH|MEDIUM|LOW",
  "source_observation": "uuid"
}
```

Priority scoring:
- HIGH: directly affects an active task or goal
- MEDIUM: in a tracked domain, frequently encountered
- LOW: peripheral, noted for future reference

---

## Step 4: APPRAISE
**Input:** Gap record
**Output:** Learning decision

Decisions:
- `LEARN` — gap is worth filling now
- `DEFER` — gap is relevant but not urgent
- `IGNORE` — gap is not worth pursuing

Scoring formula:
```
relevance = (goal_alignment × 0.3)
          + (domain_match × 0.25)
          + (frequency × 0.2)
          + (impact × 0.15)
          + (learnability × 0.1)
```

If relevance > 0.5 → LEARN
If relevance 0.2–0.5 → DEFER
If relevance < 0.2 → IGNORE

---

## Step 5: SEEK
**Input:** Gap record + learning decision
**Output:** Raw information package

Actions:
1. Identify source candidates (web search, docs, APIs, repos)
2. Rank by trust score and recency
3. Retrieve content from top candidates
4. Cross-reference across sources
5. Record provenance for every retrieved item

Budget limits:
- Max 5 sources per gap
- Max 10,000 characters per source
- Max $0.10 per gap (LLM + retrieval cost)
- Stop early if 3 sources agree

---

## Step 6: LEARN
**Input:** Raw information package
**Output:** Knowledge node(s)

Process:
1. Validate across sources (require 2+ agreement for HIGH confidence)
2. Extract the core lesson (not raw text)
3. Connect to existing knowledge graph nodes
4. Assign initial confidence (0.5 base)
5. Store with full provenance

Confidence model:
- Start: 0.5
- +0.1 per additional confirming source
- +0.15 on successful task application
- +0.05 per reinforcement over time
- -0.2 on contradiction detected
- -0.3 on source retraction

---

## Step 7: CONSOLIDATE
**Input:** All knowledge nodes
**Output:** Consolidation report

Runs periodically (e.g., nightly):

1. **Decay** — reduce confidence of unused knowledge:
   ```
   new_conf = confidence × (0.995 ^ days_since_last_access)
   ```

2. **Compress** — merge similar nodes (>80% overlap):
   - Keep the higher-confidence version
   - Record the merge in audit trail

3. **Prune** — remove low-confidence knowledge:
   - confidence < 0.2 AND not accessed in 90 days → archive
   - confidence < 0.1 → delete (after audit)

4. **Reinforce** — strengthen frequently-used knowledge:
   - Every successful application: +0.15
   - Every retrieval that uses it: +0.02

---

## Step 8: VALIDATE
**Input:** Stored knowledge + new observations
**Output:** Validation report

Periodic checks:
- Does stored knowledge still match current sources?
- Has any source been retracted or updated?
- Are confidence scores calibrated (confidence ≈ actual accuracy)?
- Has any knowledge been used successfully since last consolidation?

Failed validations → trigger re-learning (back to Step 3).
