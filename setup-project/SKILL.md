<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: setup-project
version: 0.1.0
description: |
  Research project scaffolder mode. Creates standard directory layout (experiments,
  data, paper, figures), experiment tracker TSV, ML-tailored .gitignore, config.yaml,
  research-state.yaml, findings.md, uv virtual environment with dependency install,
  and git init with initial commit. Never overwrites existing files.
  Use when: "set up", "initialize", "scaffold", "new project", "setup project". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
---

## Preamble (run first)

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_SLUG=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH | PROJECT: $_SLUG"

# Config (only show if a config file exists)
_CFG=""
if [ -f resskills.yaml ]; then _CFG="resskills.yaml"
elif [ -f "${HOME}/.resskills/config.yaml" ]; then _CFG="${HOME}/.resskills/config.yaml"
fi
if [ -n "$_CFG" ]; then
  echo "CONFIG: $_CFG"
  # Only print config values that are actually set
  _METRIC=$(grep "^primary_metric:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _DIRECTION=$(grep "^metric_direction:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _BUDGET=$(grep "^time_budget_min:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _TRAIN_CMD=$(grep "^train_command:" "$_CFG" 2>/dev/null | sed 's/^train_command: *//')
  _TRAIN_FILE=$(grep "^train_file:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _VENUE=$(grep "^venue:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  [ -n "$_METRIC" ] && echo "METRIC: $_METRIC (${_DIRECTION:-lower_is_better})"
  [ -n "$_BUDGET" ] && echo "TIME_BUDGET: ${_BUDGET}min"
  [ -n "$_TRAIN_CMD" ] && echo "TRAIN: $_TRAIN_CMD | FILE: ${_TRAIN_FILE:-train.py}"
  [ -n "$_VENUE" ] && echo "VENUE: $_VENUE"
fi

# Experiment state (only if results exist)
if [ -f experiments/results.tsv ]; then
  _EXP_COUNT=$(tail -n +2 experiments/results.tsv 2>/dev/null | wc -l | tr -d ' ')
  _BEST=$(tail -n +2 experiments/results.tsv 2>/dev/null | grep "keep" | sort -t$'\t' -k2 -n | head -1 | cut -f2)
  _LAST_STATUS=$(tail -1 experiments/results.tsv 2>/dev/null | cut -f4)
  echo "EXPERIMENTS: $_EXP_COUNT runs | BEST: ${_BEST:-none} | LAST: ${_LAST_STATUS:-none}"
fi

# Research state (only if file exists)
if [ -f research-state.yaml ]; then
  echo "--- RESEARCH STATE ---"
  head -10 research-state.yaml 2>/dev/null
  echo "--- END STATE ---"
fi

# Findings (only if file exists)
if [ -f findings.md ]; then
  _FINDINGS_LINES=$(wc -l < findings.md 2>/dev/null | tr -d ' ')
  echo "FINDINGS: ${_FINDINGS_LINES} lines"
fi

# Learnings (only if file exists)
_LEARN_DIR="${HOME}/.resskills/projects/${_SLUG}"
_LEARN_FILE="${_LEARN_DIR}/learnings.md"
if [ -f "$_LEARN_FILE" ]; then
  _LEARN_LINES=$(wc -l < "$_LEARN_FILE" 2>/dev/null | tr -d ' ')
  echo "LEARNINGS: ${_LEARN_LINES} lines"
fi
```


# /setup-project -- Initialize Research Project

You are a research project scaffolder. You create the standard directory layout,
tracking files, and Python environment so the researcher can start immediately.

---

## Steps

### 1. Create Directory Structure

```
experiments/
experiments/checkpoints/
data/
paper/
figures/
```

Create each with `mkdir -p`. Do not overwrite existing directories.

### 2. Create Experiment Tracker

Write `experiments/results.tsv` with the header line:
```
commit	val_bpb	memory_gb	status	description
```
Only create if it doesn't already exist.

### 3. Create .gitignore

Write a `.gitignore` tailored for ML research projects:
```
# Data
data/raw/
*.h5
*.hdf5
*.tfrecord

# Checkpoints & models
*.pt
*.pth
*.ckpt
*.safetensors
checkpoints/

# Logs
wandb/
runs/
*.log
run.log

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# System
.DS_Store
*.swp
```
Merge with existing `.gitignore` if one exists (append missing lines).

### 4. Copy Config

If `config.yaml` does not exist, create a minimal one:
```yaml
train_command: "python train.py"
train_file: "train.py"
primary_metric: "val_loss"
metric_direction: "lower_is_better"
time_budget_min: 10
```
If it already exists, leave it untouched.

### 5. Create research-state.yaml

```yaml
project: "<project name from directory>"
created: "<YYYY-MM-DD>"
status: "active"
hypothesis: "TBD"
research_question: "TBD"
notes: ""
```
Only create if it doesn't already exist.

### 6. Create findings.md

```markdown
# Findings

## Summary

_No findings yet. Run experiments to populate._

## Key Results

## Open Questions
```
Only create if it doesn't already exist.

### 7. Set Up Virtual Environment

```bash
uv venv .venv
source .venv/bin/activate
```

If a `pyproject.toml` exists in the project root, run `uv pip install -e ".[dev]"` or
`uv pip install -e .` (depending on whether a `dev` extra is defined).

If a `requirements.txt` exists, run `uv pip install -r requirements.txt`.

If neither exists, just create the venv.

### 8. Git Init

If not already a git repo, run `git init` and make an initial commit:
```bash
git init
git add -A
git commit -m "chore: initialize research project"
```
If already a git repo, skip this step entirely.

---

## Rules

- Never overwrite existing files. Check before writing.
- If any step fails (e.g., `uv` not installed), warn the user and continue with
  remaining steps. Do not abort the entire setup.
- Print a summary at the end listing what was created and what was skipped.

---

## Completion Status

When completing this skill's workflow, report status using one of:

- **DONE** -- All steps completed successfully. Evidence provided for each claim.
- **DONE_WITH_CONCERNS** -- Completed, but with issues you should know about. List each concern.
- **BLOCKED** -- Cannot proceed. State what is blocking and what was tried.
- **NEEDS_CONTEXT** -- Missing information required to continue. State exactly what you need.

### Escalation

It is always OK to stop and say "this is too hard for me" or "I'm not confident in this result."

Bad work is worse than no work. You will not be penalized for escalating.
- If you have attempted a task 3 times without success, STOP and escalate.
- If you are uncertain about a result that affects downstream decisions, STOP and escalate.
- If the scope exceeds what you can verify, STOP and escalate.

Escalation format:
```
STATUS: BLOCKED | NEEDS_CONTEXT
REASON: [1-2 sentences]
ATTEMPTED: [what you tried]
RECOMMENDATION: [what the user should do next]
```


## Operational Self-Improvement

Before completing, reflect on this session:
- Did any commands fail unexpectedly?
- Did you take a wrong approach and have to backtrack?
- Did you discover a project-specific quirk (data format, GPU config, library version)?
- Did something take longer than expected because of a missing config or convention?

If yes, log an operational learning for future sessions. Only log genuine discoveries
that would save 5+ minutes in a future session. Don't log obvious things or transient errors.

The learnings file is at `~/.resskills/projects/{slug}/learnings.md`. Create it if it
doesn't exist. Append under the appropriate section:

```markdown
## Techniques
- [learning] (skill, YYYY-MM-DD)

## Pitfalls
- [learning] (skill, YYYY-MM-DD)

## Insights
- [learning] (skill, YYYY-MM-DD)

## Conventions
- [learning] (skill, YYYY-MM-DD)
```

If the file already exists, append to the matching section. If the section doesn't
exist, create it. Keep entries as one-line bullets.

