<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: checkpoint
version: 0.1.0
description: |
  Research session persistence mode. Save: snapshots hypothesis, experiment count, best
  result, next steps, open questions, blockers, and git state into a timestamped JSON
  checkpoint. Resume: reads the latest checkpoint, reconstructs full context, verifies
  git state drift, and briefs you on where you left off.
  Two modes: save (default) and resume.
  Use when: "save progress", "checkpoint", "resume", "where was I", "load checkpoint". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
---

## Preamble (run first)

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_SLUG=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH | PROJECT: $_SLUG"

# Config (project-local resskills.yaml > ~/.resskills/config.yaml > pack default)
_CFG=""
if [ -f resskills.yaml ]; then _CFG="resskills.yaml"
elif [ -f "${HOME}/.resskills/config.yaml" ]; then _CFG="${HOME}/.resskills/config.yaml"
fi
if [ -n "$_CFG" ]; then
  echo "CONFIG: $_CFG"
  _METRIC=$(grep "^primary_metric:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _DIRECTION=$(grep "^metric_direction:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _BUDGET=$(grep "^time_budget_min:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _TRAIN_CMD=$(grep "^train_command:" "$_CFG" 2>/dev/null | sed 's/^train_command: *//')
  _TRAIN_FILE=$(grep "^train_file:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  _VENUE=$(grep "^venue:" "$_CFG" 2>/dev/null | cut -d: -f2 | tr -d ' ')
  echo "METRIC: ${_METRIC:-val_loss} (${_DIRECTION:-lower_is_better})"
  echo "TIME_BUDGET: ${_BUDGET:-5}min"
  echo "TRAIN: ${_TRAIN_CMD:-python train.py} | FILE: ${_TRAIN_FILE:-train.py}"
  echo "VENUE: ${_VENUE:-NeurIPS}"
else
  echo "CONFIG: none (using defaults: val_loss, 5min, python train.py, NeurIPS)"
fi

# Experiment state
if [ -f experiments/results.tsv ]; then
  _EXP_COUNT=$(tail -n +2 experiments/results.tsv 2>/dev/null | wc -l | tr -d ' ')
  _BEST=$(tail -n +2 experiments/results.tsv 2>/dev/null | grep "keep" | sort -t$'\t' -k2 -n | head -1 | cut -f2)
  _LAST_STATUS=$(tail -1 experiments/results.tsv 2>/dev/null | cut -f4)
  echo "EXPERIMENTS: $_EXP_COUNT runs | BEST: ${_BEST:-none} | LAST: ${_LAST_STATUS:-none}"
else
  echo "EXPERIMENTS: 0 runs"
fi

# Research state
if [ -f research-state.yaml ]; then
  echo "--- RESEARCH STATE ---"
  head -10 research-state.yaml 2>/dev/null
  echo "--- END STATE ---"
fi

# Findings summary
if [ -f findings.md ]; then
  _FINDINGS_LINES=$(wc -l < findings.md 2>/dev/null | tr -d ' ')
  echo "FINDINGS: ${_FINDINGS_LINES} lines"
fi

# Learnings
_LEARN_DIR="${HOME}/.resskills/projects/${_SLUG}"
_LEARN_FILE="${_LEARN_DIR}/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LEARN_COUNT=$(wc -l < "$_LEARN_FILE" 2>/dev/null | tr -d ' ')
  echo "LEARNINGS: $_LEARN_COUNT entries"
  if [ "$_LEARN_COUNT" -gt 3 ] 2>/dev/null; then
    echo "--- RECENT LEARNINGS ---"
    tail -3 "$_LEARN_FILE" 2>/dev/null
    echo "--- END LEARNINGS ---"
  fi
else
  echo "LEARNINGS: 0"
fi
```


# /checkpoint -- Save & Resume Research State

You are a research session manager. You serialize the current state of a
research project so future sessions can pick up exactly where they left off.

---

## Save Mode (default)

When the user says "checkpoint", "save state", or "save progress":

1. **Gather state** by reading:
   - `research-state.yaml` (current hypothesis, goals)
   - `experiments/results.tsv` (experiment count, best result, last status)
   - `findings.md` (key discoveries so far)
   - `git log --oneline -10` (recent commits)
   - `git status --short` (uncommitted work)
   - `git branch --show-current` (active branch)

2. **Compose checkpoint JSON** with this schema:
   ```json
   {
     "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
     "project": "<project slug>",
     "branch": "<current branch>",
     "hypothesis": "<current working hypothesis>",
     "experiment_count": <N>,
     "best_result": {"metric": "<name>", "value": <number>, "commit": "<hash>"},
     "last_status": "<keep|discard|crash>",
     "next_steps": ["<planned action 1>", "<planned action 2>"],
     "open_questions": ["<question 1>", "<question 2>"],
     "blockers": ["<blocker if any>"],
     "uncommitted_files": ["<file list>"],
     "git_head": "<full SHA>"
   }
   ```

3. **Write** to `experiments/checkpoints/YYYY-MM-DD.json`.
   - Create `experiments/checkpoints/` if it doesn't exist.
   - If a checkpoint already exists for today, append a counter: `YYYY-MM-DD_2.json`.

4. **Confirm** by printing a summary of what was saved.

---

## Resume Mode

When the user says "resume", "where was I", or "load checkpoint":

1. **Find latest checkpoint**: glob `experiments/checkpoints/*.json`, sort by name, take last.
2. **Read and parse** the JSON.
3. **Print a context briefing**:
   ```
   PROJECT: <slug> (branch: <branch>)
   LAST SESSION: <timestamp>
   HYPOTHESIS: <hypothesis>
   PROGRESS: <N> experiments, best <metric>=<value>
   NEXT STEPS:
     1. <step>
     2. <step>
   OPEN QUESTIONS:
     - <question>
   BLOCKERS:
     - <blocker>
   ```
4. **Verify git state**: compare `git_head` with current HEAD. If they differ, warn
   that commits have been made since the checkpoint.
5. **Check for uncommitted work** listed in the checkpoint. If those files still have
   changes, note it. If they've been committed, note that too.

---

## Rules

- Never modify experiment results or research state during checkpoint. Read-only except
  for writing the checkpoint file itself.
- If `experiments/results.tsv` doesn't exist, record experiment_count as 0.
- If `research-state.yaml` doesn't exist, set hypothesis to "not yet defined".
- Keep checkpoint files small. No large data blobs.
- Always use UTC timestamps.

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

```bash
_SLUG=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
_LEARN_DIR="${HOME}/.resskills/projects/${_SLUG}"
mkdir -p "$_LEARN_DIR"
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"{{SKILL_NAME}}","type":"TYPE","content":"DESCRIPTION","confidence":"high"}' >> "$_LEARN_DIR/learnings.jsonl"
```

Replace TYPE with one of: `technique` (what works), `pitfall` (what breaks),
`insight` (what we discovered), `convention` (project patterns).
Replace DESCRIPTION with a one-sentence summary.

