# Twitter Thread: Curio

## Tweet 1 (Hook)
I built an AI that learns like a child.

Not "stores everything" like current AI tools.

It detects what it doesn't know, decides if it's worth learning, finds the answer, stores the lesson, and forgets what doesn't matter.

Open source. Runs locally. 🧵

## Tweet 2 (The problem)
Every AI tool today has "memory."

But memory isn't learning.

ChatGPT stores your preferences. Claude remembers your conversation. Copilot caches your code.

None of them ask: "What should I learn next?"

## Tweet 3 (How children learn)
Children don't memorize everything. They:

1. Notice gaps ("I don't know this")
2. Decide if it matters ("Is this relevant?")
3. Seek answers ("Let me find out")
4. Store the lesson ("Now I know")
5. Forget the noise ("That wasn't important")

This is learning. Not storage.

## Tweet 4 (What Curio does)
Curio implements this exact loop:

→ Detects knowledge gaps
→ Scores relevance (LEARN / DEFER / IGNORE)
→ Searches web + local sources
→ Extracts concise lessons
→ Stores with confidence scores
→ Forgets stale knowledge
→ Tracks learning progress

## Tweet 5 (Demo)
Here's what it looks like:

$ curio teach "Auth uses JWT RS256" --domain "Auth"
$ curio observe "Auth switched to OAuth2" --source "auth_v2.py"
→ Detected CONTRADICTION (HIGH priority)

$ curio know
→ [0.80] Auth uses JWT RS256
→ [0.80] Auth switched to OAuth2 (learned from web)

It found the contradiction AND learned the update.

## Tweet 6 (Architecture)
The learning loop:

1. PERCEIVE → encounter information
2. COMPARE → match against knowledge
3. DETECT GAP → what don't I know?
4. APPRAISE → is it worth learning?
5. SEEK → find the answer
6. LEARN → store the lesson
7. CONSOLIDATE → forget the noise
8. VALIDATE → is this still correct?

8 steps. Fully autonomous.

## Tweet 7 (What makes it different)
Current AI memory:
- Stores everything → noise
- Never forgets → stale knowledge
- No gap detection → doesn't know what it doesn't know
- No confidence → can't assess its own knowledge

Curio:
- Stores only what matters
- Forgets what doesn't
- Detects gaps autonomously
- Scores confidence on everything

## Tweet 8 (Open source + local)
Fully open source. Runs locally.

Works with:
- Claude Code (MCP server)
- Cursor (MCP server)
- LM Studio (fully local, no API keys)
- CLI (standalone)

Your data never leaves your machine.

## Tweet 9 (Results)
57 tests. 40 benchmarks. All passing.

- Gap detection: works
- Contradiction detection: works
- Web search learning: works
- Confidence scoring: works
- Selective forgetting: works
- Audit trail: works

## Tweet 10 (CTA)
Star it on GitHub: [link]

Try it:
```bash
git clone [repo]
cd curio
bash quickstart.sh
```

Built by @yourhandle. Open to contributions.
