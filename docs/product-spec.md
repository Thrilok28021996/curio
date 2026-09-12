# Product Specification — Autonomous Learning AI

## Product Name
**Curio** (working title — from "curiosity")

## Tagline
*"AI that knows what it doesn't know — and learns it."*

---

## 1. Vision

Build an AI system that learns like a child: selectively, continuously, autonomously. Not a chatbot with memory. Not a RAG pipeline. A system that **detects its own knowledge gaps**, **seeks information to fill them**, **evaluates quality**, **stores what matters**, **forgets what doesn't**, and **improves over time** — with minimal human intervention.

---

## 2. Core Architecture — The Learning Loop

```
┌─────────────────────────────────────────────────────────┐
│                    THE LEARNING LOOP                     │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ 1. PERCEIVE│───▶│ 2. COMPARE│───▶│ 3. DETECT │          │
│  │ (Encounter)│    │ (Match)  │    │   GAP    │          │
│  └──────────┘    └──────────┘    └─────┬────┘          │
│                                        │                │
│  ┌──────────┐    ┌──────────┐    ┌─────▼────┐          │
│  │ 7. CONSOLI-│◀──│ 6. LEARN  │◀──│ 4. APPRAISE│          │
│  │  DATE     │    │ (Update) │    │ (Filter) │          │
│  └─────┬────┘    └──────────┘    └──────────┘          │
│        │                      ┌──────────┐              │
│        │                      │ 5. SEEK   │              │
│        ▼                      │ (Acquire) │              │
│  ┌──────────┐                └──────────┘              │
│  │ 8. VALIDATE│                                         │
│  │ (Verify)  │───── Loop back to 1 ─────▶              │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Gap Detector (Curiosity Engine)

**Purpose:** Detect what the system doesn't know or knows incorrectly.

**Input:** New information encountered (user query, document, event, conversation).

**Mechanism:**
- Compare incoming information against the knowledge graph
- Calculate **prediction error**: difference between expected and actual
- Classify gap type:
  - **UNKNOWN** — no prior knowledge exists
  - **OUTDATED** — knowledge exists but may be stale
  - **CONTRADICTORY** — new info conflicts with stored knowledge
  - **INCOMPLETE** — partial knowledge, missing key details

**Output:** Gap record with:
```json
{
  "gap_id": "uuid",
  "type": "UNKNOWN|OUTDATED|CONTRADICTORY|INCOMPLETE",
  "topic": "string",
  "confidence": 0.0-1.0,
  "source": "what triggered this gap",
  "priority": "HIGH|MEDIUM|LOW",
  "timestamp": "ISO8601"
}
```

**Priority scoring:**
- HIGH: Gap directly affects a task the system is working on
- MEDIUM: Gap is in a domain the system tracks
- LOW: Gap is peripheral, noted for future reference

**What makes this different:** Current AI either knows or doesn't know. There's no mechanism to say "I'm 60% confident about this, and I should verify." This component gives the system **self-awareness**.

---

### 3.2 Relevance Filter (Appraisal Engine)

**Purpose:** Decide whether a knowledge gap is worth filling.

**Not everything is worth learning.** A child doesn't learn every fact they encounter — they focus on what matters to their current goals and interests.

**Mechanism:**
- Evaluate gap against:
  - **Current goals** — is this relevant to what I'm trying to do?
  - **Domain relevance** — is this in my tracked domain?
  - **Frequency** — how often does this topic come up?
  - **Impact** — what's the cost of not knowing this?
  - **Learnability** — can I actually learn this from available sources?

**Relevance score formula:**
```
relevance = (goal_alignment × 0.3) + (domain_match × 0.25) + 
            (frequency × 0.2) + (impact × 0.15) + (learnability × 0.1)
```

**Output:** Decision:
```json
{
  "gap_id": "uuid",
  "decision": "LEARN|DEFER|IGNORE",
  "relevance_score": 0.0-1.0,
  "reasoning": "string",
  "suggested_sources": ["list of sources to check"]
}
```

**What makes this different:** Mem0 stores everything. This component says "this isn't worth knowing right now." Quality over quantity — like a child's brain.

---

### 3.3 Knowledge Seeker (Exploration Engine)

**Purpose:** Find and acquire information to fill validated gaps.

**Mechanism:**
- Based on gap type and suggested sources, the seeker:
  - Searches web/APIs/databases
  - Reads documents
  - Asks questions (if interaction is available)
  - Runs experiments (if tools are available)
  - Consults trusted sources (with source trust scores)

**Source selection:**
- Trust-weighted: prefer high-trust sources
- Diversity-seeking: don't rely on single source
- Recency-aware: prefer recent information for fast-changing domains

**Output:** Raw information package:
```json
{
  "gap_id": "uuid",
  "raw_info": "string",
  "sources": [
    {
      "url": "string",
      "trust_score": 0.0-1.0,
      "reliability": "PRIMARY|SECONDARY|TERTIARY",
      "recency": "ISO8601"
    }
  ],
  "extraction_timestamp": "ISO8601"
}
```

**What makes this different:** Current RAG retrieves what matches a query. This component seeks information based on **what the system needs to learn**, not what the user asked for.

---

### 3.4 Knowledge Integrator (Learning Engine)

**Purpose:** Process raw information into durable, structured knowledge.

**Mechanism:**
1. **Validate** — cross-reference across sources, check consistency
2. **Compress** — extract the core lesson, not the raw text
3. **Connect** — link to existing knowledge graph nodes
4. **Store** — persist with metadata (confidence, source, timestamp)

**Knowledge representation:**
```json
{
  "knowledge_id": "uuid",
  "content": "The lesson, not the raw data",
  "domain": "string",
  "confidence": 0.0-1.0,
  "sources": ["uuid of source records"],
  "connections": ["uuid of related knowledge nodes"],
  "created_at": "ISO8601",
  "last_reinforced": "ISO8601",
  "access_count": 0,
  "reinforcement_count": 0
}
```

**Confidence model:**
- Starts at 0.5 (initial learning)
- Increases with:
  - Multiple source confirmation (+0.1 per additional source)
  - Successful application in a task (+0.15)
  - Reinforcement over time (+0.05 per reinforcement)
- Decreases with:
  - Contradictory information (-0.2)
  - Long period without use (decay)
  - Source retraction (-0.3)

**What makes this different:** Most AI stores raw text in vectors. This component stores **lessons** — compressed, connected, confidence-tracked knowledge. Like how a child remembers "fire is hot" not "on Tuesday I touched a candle."

---

### 3.5 Memory Consolidator (Forgetting Engine)

**Purpose:** Maintain knowledge quality through selective forgetting and compression.

**Like sleep consolidation in children** — periodically review stored knowledge, strengthen useful memories, compress redundant ones, decay unused ones.

**Mechanism:**
Runs periodically (e.g., nightly):

1. **Decay** — reduce confidence of unused knowledge:
   ```
   new_confidence = confidence × (decay_rate ^ days_since_last_access)
   ```
   - Default decay_rate: 0.995 (very slow)
   - Frequently accessed knowledge decays slower
   - Knowledge tied to active goals doesn't decay

2. **Compression** — merge similar knowledge nodes:
   - If two nodes cover the same topic with >80% overlap, merge them
   - Keep the higher-confidence version
   - Record the merge in audit trail

3. **Pruning** — remove knowledge below confidence threshold:
   - Confidence < 0.2 AND not accessed in 90 days → archive
   - Confidence < 0.1 → delete (after audit)

4. **Reinforcement** — strengthen frequently-used knowledge:
   - Every successful application: +0.15 confidence
   - Every query that retrieves it: +0.02 confidence

**Output:** Consolidation report:
```json
{
  "date": "ISO8601",
  "nodes_decayed": 0,
  "nodes_compressed": 0,
  "nodes_pruned": 0,
  "nodes_reinforced": 0,
  "total_knowledge_nodes": 0,
  "avg_confidence": 0.0
}
```

**What makes this different:** This is the "quality over quantity" engine. Most AI accumulates knowledge forever. This component **actively curates** — like a child's brain deciding what to keep.

---

### 3.6 Knowledge Map (Metacognition Engine)

**Purpose:** Give the system self-awareness of what it knows, what it's unsure about, and what it doesn't know.

**Mechanism:**
Maintains a structured map of knowledge domains:

```json
{
  "domain": "Ontario Real Estate Compliance",
  "subdomains": [
    {
      "name": "TRESA Regulations",
      "confidence": 0.85,
      "knowledge_count": 47,
      "last_updated": "2026-09-10",
      "gaps_detected": 2,
      "coverage": "HIGH"
    },
    {
      "name": "RECO Advertising Rules",
      "confidence": 0.72,
      "knowledge_count": 23,
      "last_updated": "2026-08-15",
      "gaps_detected": 5,
      "coverage": "MEDIUM"
    }
  ],
  "total_coverage": 0.78,
  "active_gaps": 7,
  "last_consolidation": "2026-09-12"
}
```

**Coverage levels:**
- HIGH: confidence > 0.8, few gaps, recent updates
- MEDIUM: confidence 0.5-0.8, some gaps, or older updates
- LOW: confidence < 0.5, many gaps, or stale knowledge
- NONE: no knowledge in this domain

**What makes this different:** The system can answer questions like:
- "What do you know about X?" → gives confidence-rated summary
- "What don't you know?" → lists active gaps
- "When did you last learn about Y?" → gives recency info

This is **AI self-awareness** — something no product currently offers.

---

## 4. Product Variants

### Variant A: Compliance Bot (Broko-style)

| Component | Implementation |
|---|---|
| **Domain** | Regulatory compliance (real estate, legal, finance) |
| **Gap Detection** | Monitor regulatory feeds, detect changes |
| **Relevance Filter** | Map changes to company's specific obligations |
| **Knowledge Seeker** | Pull new regulations, extract key changes |
| **Knowledge Integrator** | Update compliance knowledge base, flag impacted policies |
| **Forgetting** | Archive superseded regulations, compress redundant guidance |
| **Metacognition** | Dashboard showing coverage by regulation area |

**Buyer:** Compliance teams at regulated companies
**Pricing:** $500-2000/mo per org

---

### Variant B: Developer/Research Agent

| Component | Implementation |
|---|---|
| **Domain** | Codebase, documentation, best practices |
| **Gap Detection** | Detect outdated patterns, missing tests, security gaps |
| **Relevance Filter** | Prioritize by codebase impact and team activity |
| **Knowledge Seeker** | Search docs, GitHub issues, Stack Overflow |
| **Knowledge Integrator** | Store lessons as code patterns, not raw text |
| **Forgetting** | Archive patterns from deprecated libraries |
| **Metacognition** | Knowledge map of codebase expertise areas |

**Buyer:** Engineering teams, individual developers
**Pricing:** $20-50/mo per seat

---

### Variant C: Personal Learning Assistant

| Component | Implementation |
|---|---|
| **Domain** | User's life, work, interests, relationships |
| **Gap Detection** | Detect when user mentions something system doesn't know |
| **Relevance Filter** | Prioritize by user's current goals and projects |
| **Knowledge Seeker** | Ask user, search web, pull from connected apps |
| **Knowledge Integrator** | Build personal knowledge graph with connections |
| **Forgetting** | Decay old context, keep active projects |
| **Metacognition** | "I know you're working on X, but I don't know Y about it" |

**Buyer:** Knowledge workers, power users
**Pricing:** $10-30/mo per user

---

## 5. Data Model

### Core Entities

```
KnowledgeNode
├── id: uuid
├── content: string (the lesson)
├── domain: string
├── subdomain: string
├── confidence: float (0.0-1.0)
├── type: FACT | PROCEDURE | PREFERENCE | RELATIONSHIP
├── sources: [SourceRecord]
├── connections: [KnowledgeNode] (graph edges)
├── created_at: timestamp
├── last_reinforced: timestamp
├── last_accessed: timestamp
├── access_count: int
├── reinforcement_count: int
└── audit_trail: [AuditEntry]

GapRecord
├── id: uuid
├── type: UNKNOWN | OUTDATED | CONTRADICTORY | INCOMPLETE
├── topic: string
├── confidence: float
├── priority: HIGH | MEDIUM | LOW
├── status: OPEN | LEARNING | RESOLVED | DEFERRED
├── created_at: timestamp
├── resolved_at: timestamp
└── resolution: string (what was learned)

SourceRecord
├── id: uuid
├── url: string
├── trust_score: float (0.0-1.0)
├── reliability: PRIMARY | SECONDARY | TERTIARY
├── last_verified: timestamp
├── access_count: int
└── accuracy_history: [float] (how often this source was correct)

DomainMap
├── domain: string
├── subdomains: [Subdomain]
├── total_confidence: float
├── coverage: HIGH | MEDIUM | LOW | NONE
├── active_gaps: int
└── last_consolidated: timestamp
```

---

## 6. API Design

### Gap Detection
```python
# System detects a knowledge gap
gap = curio.detect_gap(
    context="User asked about TRESA Section 22 amendments",
    current_knowledge=knowledge_graph
)
# Returns: GapRecord with type, priority, confidence

# Or explicitly mark a gap
curio.mark_gap(
    topic="Ontario HST Bill 114",
    type="UNKNOWN",
    priority="HIGH"
)
```

### Learning
```python
# Learn from a specific source
result = curio.learn(
    gap_id="gap-uuid",
    source_url="https://ontario.ca/bill-114",
    extract_key=True  # compress to lesson, not raw text
)
# Returns: KnowledgeNode with confidence, connections

# Learn from multiple sources (cross-validation)
result = curio.learn_multi(
    gap_id="gap-uuid",
    sources=["url1", "url2", "url3"],
    require_consensus=True  # only store if sources agree
)
```

### Knowledge Retrieval
```python
# Retrieve with confidence
result = curio.recall(
    query="What are the TRESA advertising rules?",
    min_confidence=0.7,  # only return high-confidence knowledge
    include_sources=True
)
# Returns: KnowledgeNode + source records

# Check what system knows about a domain
status = curio.status(domain="Ontario Compliance")
# Returns: DomainMap with coverage, gaps, confidence
```

### Forgetting
```python
# Manual consolidation trigger
report = curio.consolidate(
    decay_rate=0.995,
    prune_threshold=0.1,
    compression_threshold=0.8
)
# Returns: ConsolidationReport

# Check what would be forgotten
candidates = curio.forget_candidates(
    min_confidence=0.2,
    max_age_days=90
)
```

### Metacognition
```python
# What does the system know?
knowledge_map = curio.knowledge_map()
# Returns: full DomainMap tree

# What doesn't it know?
gaps = curio.active_gaps(priority="HIGH")
# Returns: [GapRecord]

# How confident is it about a specific topic?
confidence = curio.confidence(topic="TRESA Section 22")
# Returns: 0.85 with source history
```

---

## 7. Technical Stack (Recommended)

| Layer | Technology | Why |
|---|---|---|
| **Knowledge Graph** | Neo4j or Qdrant with graph extensions | Graph relationships + vector search |
| **Embeddings** | OpenAI text-embedding-3 or open-source (Mistral) | Knowledge representation |
| **Vector Store** | Qdrant or Pinecone | Fast retrieval, filtering |
| **Relational Store** | PostgreSQL | Audit trails, metadata, user data |
| **Orchestration** | Python + LangChain/LangGraph | Learning loop state machine |
| **LLM** | GPT-4/Claude for integration, smaller models for classification | Cost/quality balance |
| **Monitoring** | Prometheus + Grafana | Track learning metrics |
| **Scheduler** | Celery or APScheduler | Nightly consolidation runs |

---

## 8. Metrics & Evaluation

### Learning Metrics
| Metric | Definition | Target |
|---|---|---|
| **Gap Detection Rate** | % of knowledge gaps correctly identified | >90% |
| **Learning Accuracy** | % of stored knowledge that is factually correct | >95% |
| **Relevance Precision** | % of learned topics that were actually useful | >80% |
| **Coverage Growth** | % increase in domain coverage over time | +5%/month |
| **Confidence Calibration** | Correlation between confidence and actual accuracy | >0.8 |

### Forgetting Metrics
| Metric | Definition | Target |
|---|---|---|
| **Noise Ratio** | % of stored knowledge that is redundant or useless | <10% |
| **Compression Rate** | Knowledge nodes reduced per consolidation cycle | 5-15% |
| **Decay Accuracy** | % of pruned knowledge that was genuinely useless | >85% |
| **Knowledge Freshness** | Average age of active knowledge nodes | <30 days |

### User-Facing Metrics
| Metric | Definition | Target |
|---|---|---|
| **Self-Sufficiency** | % of gaps resolved without human input | >70% |
| **Response Quality** | User rating of answers using learned knowledge | >4.5/5 |
| **Learning Speed** | Time from gap detection to knowledge availability | <1 hour |

---

## 9. MVP Scope (Phase 1)

**Goal:** Prove the learning loop works for ONE domain.

**Features:**
1. ✅ Gap detector (detect uncertainty in responses)
2. ✅ Relevance filter (basic scoring)
3. ✅ Knowledge seeker (web search + document reading)
4. ✅ Knowledge integrator (store lessons with confidence)
5. ✅ Basic forgetting (confidence decay + pruning)
6. ✅ Knowledge map (domain coverage dashboard)

**Not in MVP:**
- ❌ Hypothesis testing / experimentation
- ❌ Social learning / trust-weighted sources
- ❌ Cross-domain transfer
- ❌ Multi-user / team features
- ❌ API for external consumers

**Domain:** Pick ONE — your strongest domain knowledge.

**Timeline:** 8-12 weeks to working MVP.

---

## 10. Revenue Model Options

| Model | Price | Best For |
|---|---|---|
| **SaaS subscription** | $20-200/mo | B2C, small teams |
| **Per-agent pricing** | $0.01-0.10/learning cycle | API/developer play |
| **Enterprise license** | $500-5000/mo | Compliance, legal, finance |
| **Open source + hosted** | Free / $99-499/mo | Community adoption + monetization |

---

## 11. Competitive Positioning

```
                    MEMORY ←──────────────→ LEARNING
                         │                      │
                    Mem0, Memori          ??? (YOUR POSITION)
                    TencentDB             
                    LangMem               
                         │                      │
                         │                      │
                    REACTIVE ←───────────→ AUTONOMOUS
                         │                      │
                    All current           YOUR PRODUCT
                    RAG systems           
```

**Position:** Top-right quadrant — **autonomous learning**, not just memory.

**One-liner:** "The first AI that learns like a child."

---

## 12. Open Design Questions

1. **Local-first or cloud?** Privacy implications, deployment complexity
2. **LLM-agnostic or provider-specific?** Flexibility vs. integration depth
3. **Open source the core?** Community adoption vs. competitive moat
4. **Single-domain or multi-domain from day 1?** Focus vs. ambition
5. **How to handle hallucination in learning?** System learns wrong things — how to detect and correct?
6. **What triggers learning?** User query? Scheduled scans? Real-time monitoring?
7. **How to measure "learning quality" objectively?** Hard problem.
