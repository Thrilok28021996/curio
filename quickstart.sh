#!/bin/bash
# Curio — Quick Start Demo
# Run: bash quickstart.sh

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║       Curio — AI That Learns Like a Child        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Clean slate
rm -f ~/.curio/knowledge.db ~/.curio/audit.jsonl

cd "$(dirname "$0")"

# Prefer the project venv: system python3 is 3.9 on macOS and cannot run the
# MCP server (mcp needs 3.10+).
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi
echo "  Using interpreter: $PY ($($PY -V 2>&1))"
echo ""

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 1: Teach Curio about your project"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src teach "This project uses FastAPI for the backend API framework" --domain "Backend"
$PY -m src teach "Authentication uses JWT with RS256 signing" --domain "Auth"
$PY -m src teach "Database is PostgreSQL with SQLAlchemy ORM" --domain "Database"
$PY -m src teach "Rate limit is 100 requests per minute per user" --domain "API"
$PY -m src teach "Deployment is on AWS ECS with Docker containers" --domain "Infrastructure"

echo ""
echo "  ✅ Taught 5 facts"
echo ""

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 2: See what Curio knows"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src know

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 3: Check confidence on a topic"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src confidence "JWT authentication"
$PY -m src confidence "quantum physics"

echo ""

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 4: Observe new information (detect gaps)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "  Observing: 'CI/CD uses GitHub Actions with 3 stages'"
$PY -m src observe "The CI/CD pipeline uses GitHub Actions with 3 stages: test, build, deploy" --source ".github/workflows/deploy.yml"

echo ""
echo "  Observing: 'Auth changed to OAuth2'"
$PY -m src observe "Authentication is no longer using JWT, now uses OAuth2 with Google and GitHub providers" --source "auth_v2.py"

echo ""

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 5: Check what Curio knows now"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src know

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 6: Check gaps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src gaps

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 7: See progress"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src progress

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 8: Run consolidation (forgetting)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src consolidate

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 9: See the audit trail"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src audit --last 10

# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 10: Store stats"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$PY -m src stats

# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║              Demo complete!                      ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Curio learned about your project, detected gaps,"
echo "found contradictions, and tracked everything."
echo ""
echo "Next steps:"
echo "  1. Point Curio at your real project"
echo "  2. Set up LM Studio for local LLM extraction"
echo "  3. Add the MCP server to Claude Code / Cursor"
echo ""
echo "Docs: docs/"
echo "Config: cp config.example.yaml ~/.curio/config.yaml"
echo ""
