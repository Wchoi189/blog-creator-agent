#!/bin/bash
# Agent-Only Artifact Creation Wrapper
# This script is ONLY for AI agents - humans should not use this

echo "🤖 Agent Artifact Creation (AGENT-ONLY)"
echo "======================================"
echo ""
echo "⚠️  WARNING: This tool is for AI agents only!"
echo "   Humans should use the main project tools."
echo ""

# Check if we're in the agent directory
if [ ! -f "Makefile" ]; then
    echo "❌ Error: This script must be run from the agent/ directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: agent/"
    exit 1
fi

# Run the artifact creation command
python ../scripts/agent_tools/core/artifact_workflow.py "$@"
