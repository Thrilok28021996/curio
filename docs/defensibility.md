# Curio — Defensibility Analysis

## The threat

With AI coding assistants (Claude Code, Cursor, Codex), a developer can ask AI to build a basic version of Curio in a weekend:

> "Build me a system that detects knowledge gaps, searches the web to fill them, stores lessons with confidence scores, and forgets old stuff."

AI would produce something that works — maybe 70% of what Curio does.

## The honest answer

**Yes, they can build it. And some will.**

This is true for every developer tool:
- People build their own CI/CD → GitLab still does $680M
- People build their own analytics → PostHog still does $45M
- People build their own databases → Supabase still does $50M

**The majority of developers would rather use a product than build a tool.**

---

## Who builds vs who uses

| Developer type | Behavior | % of market |
|---|---|---|
| **Builder** | Builds it themselves, custom | 5-10% |
| **Pragmatist** | Uses what works, configures it | 60-70% |
| **Non-technical** | Needs a product, can't build | 20-30% |

**Curio targets the 80-90% who'd rather use it.**

---

## What AI can build in a weekend

- Basic gap detection
- Store everything
- Search the web
- Store a lesson
- Delete old data
- Show a confidence score
- Log decisions
- Work on one project

## What takes months to get right

- Scoring formulas that actually work
- Knowing what to store and what to discard
- Source trust evaluation and cross-referencing
- Extracting the *right* lesson from raw text
- Principled forgetting that doesn't lose important knowledge
- Confidence calibration (confidence ≈ actual accuracy)
- Audit trail for debugging learning failures
- Multi-project, multi-domain, team contexts

---

## The 5 layers of defensibility

### 1. Battle-tested edge cases

The gap detector took 3 iterations:
- V1: keyword overlap (too simple)
- V2: negation pattern matching (missed value conflicts)
- V3: value conflict detection + expanded patterns (works)

Contradiction detection needed:
- Negation patterns (is not, doesn't, etc.)
- Replacement signals (now uses, switched to, etc.)
- Value conflict detection (X uses Y vs X uses Z)
- Temporal signals (was changed, updated to)

**A DIY version would hit these same problems and spend weeks debugging them.**

### 2. The evaluation framework

Curio has 10 benchmark tasks that validate the learning loop:
- Basic storage and retrieval
- Gap detection on unknown topics
- Contradiction detection
- Stale knowledge detection
- Confidence scoring
- Consolidation preserves important knowledge
- Multi-domain tracking
- Audit trail completeness
- Progress tracking
- Web search integration

**Without benchmarks, a DIY version has no way to know if it's learning correctly.**

### 3. The MCP integration

Curio works with Claude Code and Cursor out of the box:
```json
{
  "mcpServers": {
    "curio": {
      "command": "python",
      "args": ["-m", "src.mcp_server"]
    }
  }
}
```

**A DIY version needs custom wiring for each tool.**

### 4. The audit trail

When Curio learns the wrong thing, you can trace exactly why:
```
2026-09-12 14:32:01 | OBSERVE | content="Auth uses HMAC"
2026-09-12 14:32:02 | GAP_DETECTED | type=CONTRADICTORY | topic=auth
2026-09-12 14:32:03 | APPRAISED | decision=LEARN | relevance=0.65
2026-09-12 14:32:05 | SEEK | local=0 web=3
2026-09-12 14:32:07 | LEARNED | confidence=0.72 | sources=2
```

**A DIY version has no debugging path for learning failures.**

### 5. The consolidation engine

Forgetting is the hardest part:
- Too aggressive → lose important knowledge
- Too conservative → noise accumulates
- Wrong timing → forget things you still need

Curio's thresholds were tuned through testing:
- Decay rate: 0.995 (slow, preserves recent knowledge)
- Archive threshold: 0.2 confidence + 90 days unused
- Prune threshold: 0.1 confidence
- Compression overlap: 80%

**A DIY version would need months of real-world use to get these right.**

---

## What this means for the product

### Do's

1. **Free tier must be genuinely good** — so builders who try it say "this is better than what I'd build"
2. **Documentation must be excellent** — so non-builders can set it up easily
3. **MCP server must work perfectly** — instant value, zero configuration
4. **Benchmarks must be public** — prove the learning loop works
5. **Audit trail must be visible** — show the learning decisions in real-time

### Don'ts

1. **Don't compete on "it's hard to build"** — AI makes everything easier to build
2. **Don't hide the architecture** — open source builds trust
3. **Don't gate basic features** — free tier must be complete
4. **Don't ignore builders** — they're your best evangelists

---

## The real moat

The code is not the moat. The **refinement** is.

| Layer | What it is | How hard to replicate |
|---|---|---|
| **Code** | The learning loop implementation | Easy — AI can build it in a weekend |
| **Edge cases** | Contradiction detection, value conflicts | Medium — takes weeks of debugging |
| **Benchmarks** | 10 validated test scenarios | Hard — requires domain expertise |
| **Tuning** | Scoring formulas, decay rates, thresholds | Hard — requires months of real use |
| **Integration** | MCP server, CLI, API | Medium — requires ecosystem knowledge |
| **Trust** | Audit trail, provenance, calibration | Hard — requires proving it works |
| **Community** | Users, contributors, feedback loops | Hardest — takes years |

**The moat is layers 2-7. Layer 1 (code) is free.**

---

## The 80/20 rule of developer tools

```
80% of developers: use what works, don't build custom
20% of developers: build custom, don't use products

Of the 20% who build:
  - 15% build it, use it for a week, abandon it
  - 4% build it, use it for a month, hit problems
  - 1% build it, maintain it, make it production-ready

Of the 80% who use products:
  - 60% use free tier, never pay
  - 15% upgrade to paid for convenience
  - 5% upgrade to team/enterprise for collaboration
```

**Curio's target market is the 80% who use products, especially the 20% who upgrade to paid.**

---

## Pricing that reflects this reality

| Tier | Price | Target user | Why they pay |
|---|---|---|---|
| **Free** | $0 | Builders + casual users | Full learning loop, local |
| **Cloud** | $20/mo | Power users | Sync, dashboard, API |
| **Team** | $50/user/mo | Teams | Shared knowledge, onboarding, compliance |

**The free tier is the top of the funnel. The paid tiers are the business.**

---

## Key quote

> "The open-source project is the marketing. The cloud product is the business."
> — Paradigm for open-core companies (Supabase, PostHog, Grafana)

**For Curio: the engine is the marketing. The product is the business.**
