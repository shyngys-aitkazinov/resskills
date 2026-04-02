<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: setup-project
version: 0.2.0
description: |
  Research project scaffolder mode. Creates standard directory layout (experiments,
  data, paper, figures), .gitignore, research-state.yaml, findings.md, and uv virtual
  environment. Asks the user what they're building before creating config. Never
  overwrites existing files.
  Use when: "set up", "initialize", "scaffold", "new project", "setup project". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

## Preamble (run first)

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_SLUG=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH | PROJECT: $_SLUG"

# Config (if user has set one up)
if [ -f resskills.yaml ]; then
  echo "CONFIG: resskills.yaml"
  cat resskills.yaml
elif [ -f "${HOME}/.resskills/config.yaml" ]; then
  echo "CONFIG: ~/.resskills/config.yaml"
  cat "${HOME}/.resskills/config.yaml"
fi

# Project state: show what exists, skip what doesn't
[ -f experiments/results.tsv ] && echo "RESULTS: experiments/results.tsv ($(tail -n +2 experiments/results.tsv 2>/dev/null | wc -l | tr -d ' ') runs)"
[ -f research-state.yaml ] && echo "STATE: research-state.yaml"
[ -f findings.md ] && echo "FINDINGS: findings.md ($(wc -l < findings.md 2>/dev/null | tr -d ' ') lines)"

# Learnings (per-project, if any)
_LEARN="${HOME}/.resskills/projects/${_SLUG}/learnings.md"
[ -f "$_LEARN" ] && echo "LEARNINGS: $_LEARN ($(wc -l < "$_LEARN" 2>/dev/null | tr -d ' ') lines)"
```

Use the context above to understand the project state. If a config file exists, use its
values. If not, infer what you need from the project files, or ask the user if ambiguous.
Do not assume defaults -- understand the situation and act accordingly.

## Operating Mode

Check the config for `mode:` (defaults to `interactive` if not set).
The user can also override per-invocation by saying "run autonomously" or "autonomous mode."

**interactive** (default):
- Ask clarifying questions when input is ambiguous (use AskUserQuestion).
- Pause at human_checkpoint skills for approval before proceeding.
- Report findings and wait for direction.

**autonomous**:
- NEVER ask questions. NEVER pause. NEVER wait for approval. Do NOT use AskUserQuestion.
- When something is ambiguous, make the best decision you can from available context
  (project files, research-state.yaml, findings.md, git history, learnings).
- Log every assumption you made to `research-log.md` with tag `[ASSUMPTION]` so the
  user can review them later.
- When a skill finishes, check `research-state.yaml` next_steps and chain into the
  next skill automatically. Keep going until next_steps is empty or you hit a hard blocker.
- If truly stuck (no context to infer from, no next_steps), write the blocker to
  `research-log.md` with tag `[BLOCKED]` and stop. Do not spin.


# /setup-project -- Initialize Research Project

You are a research project scaffolder. You create directory layout, tracking files,
and Python environment so the researcher can start immediately.

---

## Step 0: Understand the project

Before creating anything, understand what the user is building. Ask if not obvious:
- What kind of project? (ML training, library, data analysis, paper, general research)
- This determines which files to create. Not every project needs a results.tsv or train.py.

## Step 1: Create Directory Structure

Always create:
```
data/
figures/
```

Only create if the project involves experiments:
```
experiments/
experiments/checkpoints/
```

Only create if the project involves paper writing:
```
paper/
```

Use `mkdir -p`. Do not overwrite existing directories.

## Step 2: Create Experiment Tracker (only if relevant)

If the project involves running experiments, create `experiments/results.tsv` with
a header row. Ask the user what metrics to track, or infer from context. Example:

```
commit	metric	status	description
```

The columns should match what the project actually measures. Do not hardcode `val_bpb`
or any specific metric name.

Only create if it doesn't already exist.

## Step 3: Create .gitignore

Write a `.gitignore` tailored for the project type. Start with Python basics:
```
__pycache__/
*.pyc
.venv/
*.egg-info/
.DS_Store
*.swp
```

Add ML-specific patterns only if the project involves model training:
```
*.pt
*.pth
*.ckpt
*.safetensors
checkpoints/
wandb/
runs/
*.log
```

Add data patterns only if relevant:
```
data/raw/
*.h5
*.hdf5
*.tfrecord
```

Merge with existing `.gitignore` if one exists (append missing lines).

## Step 4: Create Config (only if the user wants one)

Do NOT create a `resskills.yaml` by default. Only create one if:
- The user asks for it
- The project clearly needs experiment configuration

If creating one, ask the user what values to set. Do not fill in defaults silently.

## Step 5: Create research-state.yaml

```yaml
project: "<project name from directory>"
created: "<YYYY-MM-DD>"
status: "active"
notes: ""
```

Only create if it doesn't already exist.

## Step 6: Create findings.md

```markdown
# Findings

## Summary

_No findings yet._

## Key Results

## Open Questions
```

Only create if it doesn't already exist.

## Step 7: Set Up Virtual Environment

```bash
uv venv .venv
```

If `pyproject.toml` exists, run `uv sync`.
If `requirements.txt` exists, run `uv pip install -r requirements.txt`.
If neither exists, just create the venv.

## Step 8: Git Init

If not already a git repo:
```bash
git init
git add -A
git commit -m "chore: initialize project"
```

If already a git repo, skip entirely.

---

## Rules

- Never overwrite existing files. Check before writing.
- Adapt to the project type. Not every project is ML training.
- If a step fails (e.g., `uv` not installed), warn and continue.
- Print a summary at the end listing what was created and what was skipped.

---

## Persist Results

Before reporting status, save your work so future sessions can pick up where you left off.

### 1. Append to `research-log.md`

Every skill invocation MUST append a timestamped entry:

```markdown
---
### [YYYY-MM-DD HH:MM] /skill-name — one-line summary
<2-5 bullet points: what was done, key result, next action>
```

Create `research-log.md` if it doesn't exist. Always append, never overwrite.

### 2. Update `research-state.yaml`

Update only the fields your work changed:
- `timestamp`: now (ISO format)
- `project`, `branch`: from git
- `hypothesis` / `hypothesis_status`: if understanding changed
- `experiment_count`, `best_metric`, `best_commit`: if experiments ran
- `iteration_phase`: if the project phase advanced
- `open_questions`: merge new questions with existing
- `next_steps`: update with concrete next actions

Create from `templates/research-state.yaml` if it doesn't exist.

### 3. Update `findings.md` (only for confirmed results)

Only append when you have a real finding backed by evidence:
- Experiment showed a statistically significant result
- Analysis revealed a confirmed pattern
- A hypothesis was confirmed or refuted with data

Each entry: one bullet with evidence. "X because Y (metric=Z, p=W)".
Do NOT use `findings.md` for preliminary notes, plans, or speculation.
Create from `templates/findings.md` if it doesn't exist.

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

