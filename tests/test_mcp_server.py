"""Test that the Curio MCP server starts and exposes all tools."""

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

# Repo root: tests/ -> <repo>. Never hardcode a machine-specific path here,
# or the test breaks for every other clone location.
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _start_server():
    """Start the MCP server and return the Popen object."""
    return subprocess.Popen(
        [sys.executable, "-m", "src.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(_REPO_ROOT),
        env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
    )


def _mcp_init(proc):
    """Send MCP initialize + initialized, read the response."""
    proc.stdin.write((json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.1"},
        },
    }) + "\n").encode())
    proc.stdin.flush()
    time.sleep(0.5)
    ready = select.select([proc.stdout], [], [], 5)
    if not ready[0]:
        return None
    return json.loads(proc.stdout.readline().decode().strip())


def _mcp_notify(proc, method):
    proc.stdin.write((json.dumps({"jsonrpc": "2.0", "method": method, "params": {}}) + "\n").encode())
    proc.stdin.flush()


def _mcp_call(proc, req_id, method, params):
    proc.stdin.write((json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}) + "\n").encode())
    proc.stdin.flush()
    time.sleep(1)
    ready = select.select([proc.stdout], [], [], 5)
    if not ready[0]:
        return None
    return json.loads(proc.stdout.readline().decode().strip())


def _extract_text(result):
    """Extract text from MCP tool call result."""
    content = result.get("content", [])
    for item in content:
        if item.get("type") == "text":
            return item["text"]
    return None


def test_mcp_server_starts_and_lists_tools():
    """Verify the MCP server starts and exposes all 7 required tools."""
    proc = _start_server()
    try:
        init_resp = _mcp_init(proc)
        assert init_resp is not None, "No response to initialize"
        assert init_resp.get("id") == 1

        _mcp_notify(proc, "notifications/initialized")
        time.sleep(0.3)

        tools_resp = _mcp_call(proc, 2, "tools/list", {})
        assert tools_resp is not None, "No response to tools/list"
        assert tools_resp.get("id") == 2

        tools = tools_resp["result"]["tools"]
        tool_names = sorted([t["name"] for t in tools])
        expected = sorted([
            "curio_teach", "curio_observe", "curio_know",
            "curio_gaps", "curio_progress", "curio_confidence",
            "curio_consolidate",
        ])
        assert tool_names == expected, (
            f"Tools mismatch.\n  Expected: {expected}\n  Got:      {tool_names}"
        )
        print(f"PASS: Server started and exposed {len(tools)} tools: {tool_names}")
    finally:
        proc.terminate()
        proc.wait(timeout=3)


def test_curio_teach():
    """Test calling curio_teach tool via MCP protocol."""
    proc = _start_server()
    try:
        _mcp_init(proc)
        _mcp_notify(proc, "notifications/initialized")
        time.sleep(0.3)

        resp = _mcp_call(proc, 3, "tools/call", {
            "name": "curio_teach",
            "arguments": {
                "content": "Python uses dynamic typing",
                "domain": "Python",
                "confidence": 0.9,
            },
        })
        assert resp is not None, "No response to curio_teach"
        assert resp.get("id") == 3

        result = resp["result"]
        assert not result.get("isError"), f"Tool returned error: {result}"

        text = _extract_text(result)
        assert text is not None, f"No text in result: {result}"
        tool_output = json.loads(text)
        assert tool_output["status"] == "success"
        assert "knowledge_id" in tool_output
        print(f"PASS: curio_teach stored knowledge_id={tool_output['knowledge_id'][:8]}...")
    finally:
        proc.terminate()
        proc.wait(timeout=3)


def test_curio_observe():
    """Test calling curio_observe tool via MCP protocol."""
    proc = _start_server()
    try:
        _mcp_init(proc)
        _mcp_notify(proc, "notifications/initialized")
        time.sleep(0.3)

        resp = _mcp_call(proc, 4, "tools/call", {
            "name": "curio_observe",
            "arguments": {
                "content": "The project uses PostgreSQL for data storage",
                "source": "test",
                "obs_type": "event",
            },
        })
        assert resp is not None, "No response to curio_observe"
        result = resp["result"]
        assert not result.get("isError"), f"Tool returned error: {result}"
        text = _extract_text(result)
        tool_output = json.loads(text)
        assert tool_output["status"] == "success"
        print(f"PASS: curio_observe detected {tool_output['gaps_detected']} gap(s)")
    finally:
        proc.terminate()
        proc.wait(timeout=3)


def test_curio_know_and_progress():
    """Test curio_know and curio_progress tools."""
    proc = _start_server()
    try:
        _mcp_init(proc)
        _mcp_notify(proc, "notifications/initialized")
        time.sleep(0.3)

        # know
        resp = _mcp_call(proc, 5, "tools/call", {
            "name": "curio_know",
            "arguments": {"top_n": 5},
        })
        result = resp["result"]
        text = _extract_text(result)
        tool_output = json.loads(text)
        assert tool_output["status"] == "success"
        print(f"PASS: curio_know returned {tool_output['count']} items")

        # progress
        resp = _mcp_call(proc, 6, "tools/call", {
            "name": "curio_progress",
            "arguments": {},
        })
        result = resp["result"]
        text = _extract_text(result)
        tool_output = json.loads(text)
        assert tool_output["status"] == "success"
        print(f"PASS: curio_progress returned successfully")
    finally:
        proc.terminate()
        proc.wait(timeout=3)


if __name__ == "__main__":
    test_mcp_server_starts_and_lists_tools()
    test_curio_teach()
    test_curio_observe()
    test_curio_know_and_progress()
    print("\nAll tests passed!")
