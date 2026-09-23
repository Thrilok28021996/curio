# Curio + LM Studio Setup Guide

## Fully local, no cloud, no API keys

```
┌─────────────────────────────────────────────────┐
│                 LM Studio                        │
│  ┌───────────────────────────────────────────┐  │
│  │  Chat with a local LLM                    │  │
│  │  (Llama 3, Mistral, Qwen, etc.)          │  │
│  └───────────────────┬───────────────────────┘  │
│                      │                           │
│                      │ MCP tools                 │
│                      ▼                           │
│  ┌───────────────────────────────────────────┐  │
│  │  Curio MCP Server                         │  │
│  │  - curio_teach                            │  │
│  │  - curio_observe                          │  │
│  │  - curio_know                             │  │
│  │  - curio_gaps                             │  │
│  │  - curio_progress                         │  │
│  │  - curio_confidence                       │  │
│  │  - curio_consolidate                      │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  All running on YOUR machine. Nothing leaves.    │
└─────────────────────────────────────────────────┘
```

## Setup (2 minutes)

### 0. Create the environment (once)

The MCP server needs Python 3.10+ — the `mcp` SDK publishes no release for 3.9
or older, so `pip install mcp` fails outright on system Python.

```bash
cd /path/to/curio
python3 -m venv .venv
.venv/bin/pip install -e .      # installs mcp>=2.0 and the curio-mcp script
```

### 1. Start LM Studio
Load a model (Llama 3.1, Mistral, Qwen 2.5, etc.)

### 2. Copy the MCP config

```bash
# Copy the example config to LM Studio's MCP directory
cp /path/to/curio/lmstudio-mcp.json ~/.lmstudio/mcp.json
```

`lmstudio-mcp.json` ships with this machine's absolute paths. If you cloned
elsewhere, change `command`, `cwd` and `PYTHONPATH` to your own clone path —
`command` must be the venv interpreter (`.venv/bin/python`), never bare `python3`.

Or manually add to `~/.lmstudio/mcp.json`:

```json
{
  "mcpServers": {
    "curio": {
      "command": "/path/to/curio/.venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/curio",
      "env": {
        "PYTHONPATH": "/path/to/curio",
        "CURIO_LLM_PROVIDER": "lmstudio",
        "CURIO_LLM_BASE_URL": "http://localhost:1234/v1",
        "CURIO_LLM_API_KEY": "lm-studio"
      }
    }
  }
}
```

Notes on the three fields that matter:
- `command` — absolute path to `.venv/bin/python`. Bare `python3` on macOS is
  3.9, which cannot install `mcp` at all.
- `cwd` — absolute path. Never `~/...`; JSON does not tilde-expand.
- `PYTHONPATH` — makes the server start even if your MCP client ignores `cwd`
  (Cursor/LM Studio-style configs do not guarantee it).

### 3. Restart LM Studio

LM Studio will automatically start the Curio MCP server.

### 4. Use it in chat

In LM Studio's chat, you can now say:

```
Teach Curio that this project uses FastAPI
```

LM Studio will call `curio_teach` automatically.

```
What does Curio know about authentication?
```

LM Studio will call `curio_know` and show the results.

```
Observe that the database was switched to MySQL
```

LM Studio will call `curio_observe` and detect gaps.

## What happens under the hood

1. You type a message in LM Studio
2. LM Studio's local LLM decides which Curio tool to call
3. Curio's MCP server executes the tool
4. The result goes back to the LLM
5. LLM responds to you with the result

**Everything stays local. Your data never leaves your machine.**

## Example conversation

```
You: Teach Curio that the API uses JWT RS256 auth

[LM Studio calls curio_teach]
[Curio stores the knowledge]
[LM Studio responds]

LM Studio: Done. I've taught Curio that the API uses JWT RS256 auth.
           Confidence: 0.80, Domain: Auth.

You: What does Curio know?

[LM Studio calls curio_know]
[Curio returns knowledge nodes]
[LM Studio responds]

LM Studio: Curio knows 5 things about your project:
           1. [0.80] API uses JWT RS256 auth
           2. [0.80] Backend uses FastAPI
           ...

You: I just found out we switched to OAuth2

[LM Studio calls curio_observe]
[Curio detects CONTRADICTION with stored JWT knowledge]
[LM Studio responds]

LM Studio: Curio detected a CONTRADICTION! 
           Stored: "API uses JWT RS256 auth"
           New: "Switched to OAuth2"
           Priority: HIGH
           Should I update the knowledge?
```

## Troubleshooting

**MCP server not starting?**
```bash
# Test Curio MCP server directly, with the same interpreter the config uses
cd /path/to/curio
.venv/bin/python -m src.mcp_server
# Ctrl-C to exit. A ModuleNotFoundError here means the venv is missing mcp.
```

**`ModuleNotFoundError: No module named 'mcp'`**
Your config is launching the wrong interpreter. `mcp` needs Python 3.10+; on
macOS system `python3` (3.9) it is uninstallable. Point `command` at
`.venv/bin/python` and re-run the test above.

**LM Studio can't find the tools?**
- Make sure LM Studio is restarted after adding the config
- Check that `command` is an absolute path to `.venv/bin/python` (a bare
  `python3` picks up system 3.9, and GUI apps often have a minimal PATH)
- Check that the `cwd` path is correct and absolute — no `~`
- Keep `PYTHONPATH` set so the server starts even if `cwd` is ignored

**Tools not appearing in chat?**
- LM Studio needs to support MCP tool calling
- Make sure you're using a model that supports tool use
- Check LM Studio version (0.3.17+ for MCP support)
