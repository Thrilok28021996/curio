# Show HN: Curio – AI that learns like a child (open source)

I built Curio, an autonomous learning AI agent that detects what it doesn't know and learns it.

**The problem:** Every AI tool today has memory — they store what you tell them. But none of them decide what's worth learning. They don't know what they don't know. They don't forget what doesn't matter.

**How children learn:**
1. They notice gaps in their knowledge ("I don't know this")
2. They decide if it's worth learning ("Is this relevant?")
3. They seek information ("Let me find out")
4. They store the lesson ("Now I know this")
5. They forget the noise ("That wasn't important")

**Curio does the same thing:**

```
$ curio teach "Auth uses JWT RS256" --domain "Auth"
Stored knowledge: confidence 0.80

$ curio observe "Auth switched to OAuth2" --source "auth_v2.py"
Detected 1 gap(s):
  [HIGH] CONTRADICTORY: Auth

$ curio know
Top 2 knowledge nodes:
  [0.80] Auth uses JWT RS256
  [0.80] Auth switched to OAuth2 (learned from web search)

$ curio progress
Active knowledge: 8 | Sources: 12 | Avg confidence: 0.80
```

**What makes it different:**
- Gap detection — knows what it doesn't know
- Selective learning — decides what's worth learning
- Web search — finds answers automatically
- Confidence scoring — rates its own knowledge
- Principled forgetting — removes stale information
- Full audit trail — every decision is logged

**Tech stack:**
- Python, SQLite, DuckDuckGo search
- MCP server for Claude Code / Cursor
- Works with LM Studio (fully local, no API keys)
- 57 tests, 40 benchmarks, all passing

**Try it:**
```bash
git clone https://github.com/yourusername/curio
cd curio
bash quickstart.sh
```

GitHub: [link]
Docs: [link]
