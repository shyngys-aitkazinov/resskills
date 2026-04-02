<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: careful
version: 0.1.0
description: |
  Research data safety guardrail mode. Pre-tool hook intercepts every bash command and
  blocks destructive patterns: rm -rf on experiments/checkpoints/data, git reset --hard,
  git push --force, eval script overwrites. Allows safe exceptions (pycache, node_modules,
  build artifacts). Session-scoped activation.
  Use when: "be careful", "safety mode", "protect my data", "guardrails on". (resskills)
allowed-tools:
  - Bash
  - Read
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
---

# /careful -- Research Data Guardrails

Safety mode is now **active**. Every bash command will be checked for destructive
patterns before running. If a destructive command is detected, you'll be warned
and can choose to proceed or cancel.

## What's Protected

| Pattern | Example | Risk |
|---------|---------|------|
| `rm -rf experiments/` | Deletes all experiment results | Data loss |
| `rm -rf checkpoints/` | Deletes model checkpoints | Data loss |
| `rm -rf data/` | Deletes datasets | Data loss |
| `rm results.tsv` | Deletes experiment log | Data loss |
| `rm -rf` / `rm -r` / `rm --recursive` | Recursive delete | Data loss |
| `git reset --hard` | Discards uncommitted work | Work loss |
| `git checkout .` / `git restore .` | Discards uncommitted changes | Work loss |
| `git push --force` / `-f` | Rewrites remote history | History loss |
| Overwriting `eval.py` / `prepare.py` | Breaks reproducibility | Integrity |

## Safe Exceptions

These patterns are allowed without warning:
- `rm -rf __pycache__` / `.cache` / `build` / `dist` / `.mypy_cache` / `.ruff_cache`
- `rm -rf node_modules` / `.next` / `.turbo` / `coverage`
- `rm -rf .venv` (virtual environment rebuild)

## How It Works

The hook reads the command from the tool input JSON, checks against the patterns
above, and returns `permissionDecision: "ask"` with a warning if a match is found.
You can always override the warning and proceed.

To deactivate, end the conversation or start a new one. Hooks are session-scoped.
