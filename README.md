# Curio

**AI that knows what it doesn't know — and learns it.**

Curio is an autonomous learning agent that detects knowledge gaps, seeks information to fill them, evaluates quality, stores what matters, forgets what doesn't, and tracks learning progress — with minimal human intervention.

## Product Path

```text
Developer learning agent  (you are here)
        ↓
General learning engine / SDK
        ↓
Personal learning assistant
        ↓
Optional vertical applications
```

## The Learning Loop

```text
1. PERCEIVE  → Encounter new information
       ↓
2. COMPARE   → Does this match what I know?
       ↓
3. DETECT GAP → "I don't know this" or "I was wrong"
       ↓
4. APPRAISE  → Is this worth learning? (relevance filter)
       ↓
5. SEEK      → Find the information (ask, search, explore)
       ↓
6. LEARN     → Update knowledge, form connections
       ↓
7. CONSOLIDATE → Strengthen what's useful, forget what's not
       ↓
8. VALIDATE  → "Do I still know this correctly?"
       ↓
   (Loop back to 1)
```

## Project Structure

```
curio/
├── src/                  ← source code
├── data/                 ← knowledge store (gitignored)
├── eval/                 ← benchmark & evaluation
├── tests/                ← unit tests
├── docs/                 ← specs, validation reports, IP boundary
├── task_plan.md          ← product plan
├── TODO.md               ← actionable checklist
├── findings.md           ← research findings
└── progress.md           ← session log
```

## Quick Start

```bash
# Clone / open
cd ~/workspace/curio

# Read the plan
cat task_plan.md

# Read the IP boundary
cat docs/IP_BOUNDARY.md

# See what's next
cat TODO.md
```

## Status

- [x] Vision and learning-loop concept defined
- [x] Market validation completed
- [x] Closest prior art reviewed
- [x] Product path decided: developer-first
- [ ] Choose independent developer use case
- [ ] Define evaluation benchmark
- [ ] Build research prototype
- [ ] Run controlled experiments
- [ ] Decide whether to productize

## License

Private — not yet licensed.
