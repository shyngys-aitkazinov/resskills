#!/usr/bin/env bash
# Hook script for /careful skill.
# Reads the Bash command from tool input JSON (stdin) and checks for destructive patterns.
# Returns JSON with permissionDecision: "allow" or "ask".

set -euo pipefail

# Read the tool input from stdin
INPUT=$(cat)

# Extract the command string from JSON
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('input',{}).get('command',''))" 2>/dev/null || echo "")

if [ -z "$COMMAND" ]; then
    echo '{"permissionDecision":"allow"}'
    exit 0
fi

# Safe exceptions: build artifacts that are always OK to delete
SAFE_PATTERNS=(
    "rm -rf __pycache__"
    "rm -rf .cache"
    "rm -rf build"
    "rm -rf dist"
    "rm -rf .mypy_cache"
    "rm -rf .ruff_cache"
    "rm -rf node_modules"
    "rm -rf .next"
    "rm -rf .turbo"
    "rm -rf coverage"
    "rm -rf .venv"
    "rm -rf .pytest_cache"
)

for safe in "${SAFE_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$safe"* ]]; then
        echo '{"permissionDecision":"allow"}'
        exit 0
    fi
done

# Dangerous patterns
DANGEROUS_PATTERNS=(
    "rm -rf experiments"
    "rm -rf checkpoints"
    "rm -rf data/"
    "rm -r experiments"
    "rm -r checkpoints"
    "rm -r data/"
    "rm results.tsv"
    "rm experiments/results.tsv"
    "rm -rf"
    "rm -r "
    "rm --recursive"
    "git reset --hard"
    "git checkout ."
    "git restore ."
    "git push --force"
    "git push -f"
    "git clean -f"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        MSG="WARNING: Destructive command detected: '$pattern'. This could delete research data. Are you sure?"
        echo "{\"permissionDecision\":\"ask\",\"message\":\"$MSG\"}"
        exit 0
    fi
done

# No dangerous pattern found
echo '{"permissionDecision":"allow"}'
