# Curio

**AI that knows what it doesn't know — and learns it.**

Curio is an autonomous learning agent that detects knowledge gaps, seeks information to fill them, evaluates quality, stores what matters, forgets what doesn't, and tracks learning progress — with minimal human intervention.

<a href="https://lmstudio.ai/install-mcp?name=curio&config=eyJjb21tYW5kIjoiY3VyaW8tbWNwIiwiYXJncyI6W119"><img src="https://files.lmstudio.ai/deeplink/mcp-install-light.svg" alt="Add MCP Server curio to LM Studio" /></a>

> **The button registers the command `curio-mcp`, which must already be on your
> PATH.** `curio-ai` is *not on PyPI yet*, so today the only way to get that command
> is to install from a clone (see Quick start) and expose that environment's `bin/`
> directory to LM Studio.
>
> If LM Studio reports the server as failed, edit `~/.lmstudio/mcp.json` and point
> `command` at your absolute interpreter path instead — the reliable option until the
> package is published. See [docs/lmstudio-setup.md](docs/lmstudio-setup.md).


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

Requires **Python 3.10+** — the `mcp` SDK publishes no release for 3.9 or older, so on
macOS system `python3` an install fails with *No matching distribution found*. Install
from a clone:

```bash
git clone https://github.com/Thrilok28021996/curio.git
cd curio
python3 -m venv .venv
.venv/bin/pip install -e .
bash quickstart.sh
```

`mcp>=2.0` is a hard dependency, so the MCP server works straight after that install.

> `pip install curio-ai` does not work yet — the package has not been published to
> PyPI. It replaces the block above once it is.

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
      "command": "curio-mcp",
      "args": [],
      "env": {
        "PYTHONPATH": "/path/to/curio"
      }
    }
  }
}
```

`curio-mcp` is the console script an install creates — but until `curio-ai` is on
PyPI it exists only inside an environment you built from a clone. The
absolute-interpreter form below always works, and `PYTHONPATH` keeps it from
depending on the client honoring `cwd`:

```json
{
  "mcpServers": {
    "curio": {
      "command": "/path/to/curio/.venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "env": { "PYTHONPATH": "/path/to/curio" }
    }
  }
}
```

### LM Studio (fully local)

Click the install button above, or copy `lmstudio-mcp.json` into place:

```bash
cp lmstudio-mcp.json ~/.lmstudio/mcp.json
# edit "command"/"cwd"/"PYTHONPATH" to your own clone path, then restart LM Studio
```

Curio also reads these env vars, so it can call your local model:

```bash
export CURIO_LLM_PROVIDER=lmstudio
export CURIO_LLM_BASE_URL=http://localhost:1234/v1
curio observe "Something new" --source "file.py"
```

**With Altra (LM Studio's fact-checking plugins):**

Altra is a *separate* LM Studio plugin family (`altra/web-search`, `altra/research`) — not
part of Curio. Install `altra/web-search` from LM Studio Hub for cross-source verification:
it reads full pages, reranks with `nomic-embed-text`, counts independent publishers, and
exposes `fact_check` / `verify_statistic`.

Chained with Curio in one chat, the flow is:

```
curio_observe   → detects a contradiction / gap
Altra search    → reads pages, fact-checks across sources
curio_teach     → stores the verified lesson with a confidence score
```

Two things to know:
- The chain is **driven by the model**, not by Curio. No Curio code calls Altra — success
  depends on the local model choosing to sequence the three tools.
- `curio_observe` already triggers Curio's **own** DuckDuckGo search (`knowledge_seeker`)
  when it finds a gap. If Altra is installed too you get two independent searches with
  two different provenance models. Prefer Altra for verification; keep Curio's built-in
  path for offline/no-Altra setups (requires the `web` extra:
  `.venv/bin/pip install ".[web]"`).

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
.venv/bin/python tests/test_core.py
.venv/bin/python tests/test_validation.py
.venv/bin/python tests/test_mcp_server.py

# Run benchmarks
.venv/bin/python eval/run_benchmark.py
```

**22 tests, 80 assertions — all passing.**

40 benchmarks. The web-search benchmarks hit live search, so results vary run to run —
expect 39–40 / 40, with `bench-027` the usual casualty when a search backend drops
the connection. A green run is not proof of a code change.

## License

**MIT-derived with a required attribution clause — not plain MIT.** See [LICENSE](LICENSE).

The attribution term is deliberate: shipping Curio puts "Powered by Curio" in front of
your users. PyPI therefore does **not** carry the `OSI Approved :: MIT License` classifier
for this package — plain MIT has no usage obligations beyond retaining the notice.

You can:
- Use it commercially
- Modify it
- Redistribute it, including in proprietary software

You must (unless exempt below):
- Keep the copyright notice and the license text
- Show a visible **"Powered by Curio"** or **"Built with Curio"** notice in your product's
  UI, README, or documentation — or link this repository from your docs / about page.
  This covers commercial products, open source projects that depend on Curio, and
  internal tools deployed within organizations.

Not required for:
- Personal, private use with no external distribution
- Contributions back to the Curio project itself

## Contributing

Contributions welcome! Open an issue or submit a PR.
