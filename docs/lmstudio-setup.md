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

### 1. Start LM Studio
Load a model (Llama 3.1, Mistral, Qwen 2.5, etc.)

### 2. Copy the MCP config

```bash
# Copy the example config to LM Studio's MCP directory
cp ~/workspace/curio/lmstudio-mcp.json ~/.lmstudio/mcp.json
```

Or manually add to `~/.lmstudio/mcp.json`:

```json
{
  "mcpServers": {
    "curio": {
      "command": "python3",
      "args": ["-m", "src.mcp_server"],
      "cwd": "~/curio",
      "env": {
        "CURIO_LLM_PROVIDER": "lmstudio",
        "CURIO_LLM_BASE_URL": "http://localhost:1234/v1",
        "CURIO_LLM_API_KEY": "lm-studio"
      }
    }
  }
}
```

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
# Test Curio MCP server directly
cd ~/workspace/curio
python3 -m src.mcp_server
```

**LM Studio can't find the tools?**
- Make sure LM Studio is restarted after adding the config
- Check that `python3` is in your PATH
- Check that the `cwd` path is correct

**Tools not appearing in chat?**
- LM Studio needs to support MCP tool calling
- Make sure you're using a model that supports tool use
- Check LM Studio version (0.3.17+ for MCP support)
