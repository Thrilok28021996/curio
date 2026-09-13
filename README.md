# Curio

**AI that knows what it doesn't know — and learns it.**

Curio is an autonomous learning agent that detects knowledge gaps, seeks information to fill them, evaluates quality, stores what matters, forgets what doesn't, and tracks learning progress — with minimal human intervention.

```
$ curio teach "Auth uses JWT RS256" --domain "Auth"
$ curio observe "Auth switched to OAuth2" --source "auth_v2.py"
Detected 1 gap(s):
  [HIGH] CONTRADICTORY: Auth

$ curio know
[0.80] Auth uses JWT RS256
[0.80] Auth switched to OAuth2 (learned from web)
```

## How it works

Curio implements a learning loop inspired by how children learn:

```
1. PERCEIVE  → encounter new information
2. COMPARE   → match against existing knowledge
3. DETECT GAP → "I don't know this"
4. APPRAISE  → "Is it worth learning?"
5. SEEK      → find the answer (web search)
6. LEARN     → store the lesson
7. CONSOLIDATE → forget what doesn't matter
8. VALIDATE  → "Is this still correct?"
```

## Quick start

```bash
# Install
pip install curio-ai

# Or clone and run directly
git clone https://github.com/yourusername/curio
cd curio
bash quickstart.sh
```

## Usage

```bash
# Teach Curio something
curio teach "The API uses FastAPI" --domain "Backend"

# Observe new information (detects gaps)
curio observe "The API switched to Flask" --source "app.py"

# See what Curio knows
curio know

# See what Curio doesn't know
curio gaps

# Check confidence on a topic
curio confidence "FastAPI"

# See learning progress
curio progress

# Run forgetting cycle
curio consolidate

# View audit trail
curio audit --last 10
```

## Works with your tools

### MCP Server (Claude Code / Cursor)

```json
// .claude/settings.json
{
  "mcpServers": {
    "curio": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/curio"
    }
  }
}
```

### LM Studio (fully local)

```bash
export CURIO_LLM_PROVIDER=lmstudio
export CURIO_LLM_BASE_URL=http://localhost:1234/v1
curio observe "Something new" --source "file.py"
```

### Python API

```python
from src.curio import Curio

curio = Curio()
curio.teach("Fact about my project", domain="project")
curio.observe("New information", source="file.py")
print(curio.know())
print(curio.gaps())
curio.close()
```

## What makes it different

| Feature | Other AI tools | Curio |
|---|---|---|
| Stores everything | ✅ | ❌ |
| Detects knowledge gaps | ❌ | ✅ |
| Decides what to learn | ❌ | ✅ |
| Forgets stale knowledge | ❌ | ✅ |
| Tracks learning progress | ❌ | ✅ |
| Confidence scoring | ❌ | ✅ |
| Full audit trail | ❌ | ✅ |
| Runs locally | ❌ | ✅ |

## Architecture

```
src/
├── models.py              # Data types
├── curio.py               # Main orchestrator
├── gap_detector.py        # Curiosity engine
├── relevance_filter.py    # Appraisal engine
├── knowledge_seeker.py    # Exploration engine
├── knowledge_integrator.py # Learning engine
├── memory_consolidator.py # Forgetting engine
├── knowledge_map.py       # Metacognition engine
├── knowledge_store.py     # SQLite storage
├── audit_log.py           # Decision trail
├── llm.py                 # LLM integration
├── web_search.py          # DuckDuckGo search
├── mcp_server.py          # MCP server
└── cli.py                 # Command line
```

## Testing

```bash
# Run all tests
python tests/test_core.py
python tests/test_validation.py

# Run benchmarks
python eval/run_benchmark.py
```

**57 tests. 40 benchmarks. All passing.**

## License

MIT — use it however you want.

## Contributing

Contributions welcome! Open an issue or submit a PR.
