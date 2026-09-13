# Reddit post for r/LocalLLaMA

**Title:** I built an AI that learns like a child — works with LM Studio + Altra (open source)

**Body:**

Hey everyone,

I built Curio, an autonomous learning AI agent that works as an MCP server with LM Studio.

**What it does:**
- Detects what it doesn't know (gap detection)
- Decides if it's worth learning (relevance scoring)
- Searches the web via Altra for verified answers
- Stores concise lessons with confidence scores
- Forgets stale knowledge automatically
- Tracks learning progress over time

**Why it's different from "memory":**
Most AI tools store everything you tell them. Curio doesn't. It detects gaps, evaluates relevance, and only keeps what matters. It's like having a junior developer who gets smarter every week.

**How it works with LM Studio:**

1. Start LM Studio, load any model
2. Click "Add to LM Studio" (one-click install)
3. Chat naturally — Curio learns automatically

```bash
# Or install manually
git clone https://github.com/Thrilok28021996/curio.git
cd curio
cp lmstudio-mcp.json ~/.lmstudio/mcp.json
# Restart LM Studio
```

**Example conversation:**

```
You: "Teach Curio that the API uses FastAPI"
→ Stored: confidence 0.80

You: "Observe that main.py imports Flask"
→ Detected: CONTRADICTORY (HIGH priority)
→ "Curio found a contradiction: stored FastAPI, observed Flask"

You: "It's Flask now, we migrated"
→ Curio updates knowledge, archives old info
```

**Fully local. No API keys. No cloud. Your data never stays on your machine.**

GitHub: https://github.com/Thrilok28021996/curio

Would love feedback from the LM Studio community!
