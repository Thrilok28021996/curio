# Curio + LM Studio: AI That Learns Like a Child

## The setup (2 minutes)

1. Start LM Studio, load any model (Llama 3, Mistral, Qwen, etc.)
2. Click the "Add to LM Studio" button below
3. Start chatting — Curio learns automatically

[![Add to LM Studio](https://lmstudio.ai/badge-add-to-lm-studio.svg)](lmstudio://add_mcp?name=curio&config=eyJjb21tYW5kIjoicHl0aG9uMyIsImFyZ3MiOlsiLW0iLCJzcmMubWNwX3NlcnZlciJdLCJlbnYiOnsiQ1VSSU9fTExNX1BST1ZJREVSIjoibG1zdHVkaW8iLCJDVVJJT19MTE1fQkFTRV9VUkwiOiJodHRwOi8vbG9jYWxob3N0OjEyMzQvdjEiLCJDVVJJT19MTE1fQVBJX0tFWSI6ImxtLXN0dWRpbyJ9fQ==)

## What happens when you use both

```
You: "What does Curio know about my project?"

LM Studio (with Curio MCP):
→ Calls curio_know
→ Returns knowledge graph with confidence scores
→ You see what Curio has learned

You: "We switched from JWT to OAuth2"

LM Studio (with Curio MCP + Altra):
→ Calls curio_observe
→ Curio detects CONTRADICTION with stored JWT knowledge
→ LLM uses Altra to verify the change
→ Curio updates knowledge with verified source
→ You see the contradiction flagged + knowledge updated
```

## The stack

```
┌─────────────────────────────────────────┐
│  You (user)                              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  LM Studio (local LLM)                  │
│  + Altra (fact-checking)                │
└────────────────┬────────────────────────┘
                 │ MCP tools
┌────────────────▼────────────────────────┐
│  Curio MCP Server                       │
│  - curio_teach                          │
│  - curio_observe                        │
│  - curio_know                           │
│  - curio_gaps                           │
│  - curio_progress                       │
│  - curio_confidence                     │
│  - curio_consolidate                    │
└─────────────────────────────────────────┘

Everything runs on YOUR machine.
Your data never leaves.
No API keys needed.
```

## What Curio gives you

| Feature | Without Curio | With Curio |
|---|---|---|
| Remembers facts | ✅ (chat only) | ✅ (persistent) |
| Detects knowledge gaps | ❌ | ✅ |
| Decides what to learn | ❌ | ✅ |
| Searches web | ❌ (or Altra only) | ✅ (with Altra) |
| Stores lessons | ❌ | ✅ (confidence-scored) |
| Forgets noise | ❌ | ✅ |
| Tracks learning progress | ❌ | ✅ |
| Audit trail | ❌ | ✅ |

## Example: Learning your codebase

```
You: "Teach Curio that the API uses FastAPI"
→ Stored: confidence 0.80

You: "Observe that main.py imports Flask"
→ Gap detected: CONTRADICTORY (HIGH)
→ "Curio found a contradiction: stored FastAPI, observed Flask"

You: "Which is correct?"
→ Curio: confidence FastAPI=0.80, Flask=0.80
→ "Both have equal confidence. You should verify."

You: "It's Flask now, we migrated"
→ Curio updates knowledge, Flask becomes primary
→ Old FastAPI knowledge archived
```

## Why LM Studio users love Curio

1. **Fully local** — no API keys, no cloud, no data leaving your machine
2. **Persistent memory** — LM Studio forgets between sessions. Curio doesn't.
3. **Self-aware** — Curio knows what it doesn't know
4. **Fact-checked** — Altra verifies what Curio learns
5. **Works out of the box** — one click to install, one command to use

## Links

- GitHub: https://github.com/Thrilok28021996/curio
- Docs: https://github.com/Thrilok28021996/curio#readme
- LM Studio: https://lmstudio.ai
