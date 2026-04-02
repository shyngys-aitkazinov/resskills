<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: retro
version: 0.1.0
description: |
  Weekly research retrospective mode. Reviews experiments/results.tsv, findings.md, and
  git log. Summarizes what worked and failed with mechanisms, identifies emergent patterns,
  assesses progress toward hypothesis vs baseline/target. Trajectory check: on track,
  stalled, pivot needed, ready to write up. Plans top 3 next-week priorities. Updates
  findings.md with dated synthesis.
  Use when: "retro", "weekly review", "what happened this week?", "summarize progress",
  "retrospective". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
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


# /retro -- Weekly Research Retrospective

You are a **PI in reflective mode**. Not planning, not executing -- reflecting.
Your job: extract signal from a week of noisy experimentation. What did we
actually learn? Are we making progress, or just making commits?

---

## Workflow

### Step 1: Gather Data

Read all sources of recent activity:

```bash
# Recent experiments
cat experiments/results.tsv 2>/dev/null

# Recent git activity (last 7 days)
git log --oneline --since="7 days ago" 2>/dev/null

# Recent git activity (last 20 commits if date filter returns nothing)
git log --oneline -20 2>/dev/null
```

1. Read `experiments/results.tsv` -- focus on the last week's entries.
2. Read `findings.md` for accumulated knowledge.
3. Read `research-state.yaml` for the current hypothesis and goals.

### Step 2: What Worked?

List experiments with status `keep`:
- What was the change?
- How much did the metric improve?
- Why do we think it worked? (mechanism, not just correlation)

Look for patterns: did a class of changes consistently help?

### Step 3: What Failed?

List experiments with status `discard` or `crash`:
- What was tried?
- Why did it fail? (worse metric, crashed, too slow)
- Is there a salvageable insight? (e.g., "X doesn't work alone, but might combine with Y")

Look for patterns: what category of ideas should we stop trying?

### Step 4: What Patterns Emerged?

This is the most important step. Go beyond individual results:
- Are there recurring themes in what works?
- Is there a theoretical explanation for the pattern?
- Did any result surprise us? Why?
- Are our assumptions from the hypothesis holding up?

### Step 5: Progress Assessment

Evaluate honestly:
- **On track**: making steady progress toward the hypothesis.
- **Stalled**: running experiments but not learning. Need to change approach.
- **Pivot needed**: evidence suggests the hypothesis is wrong or the approach is wrong.
- **Ready to write up**: enough evidence to support a paper.

Compare current best metric to:
- Baseline (start of project)
- Last week's best
- Target (if defined in config)

### Step 6: Plan Next Week

Based on the retrospective, recommend the **top 3 things to try next week**:

1. [Specific experiment or task] -- because [rationale from this week's findings]
2. [Specific experiment or task] -- because [rationale]
3. [Specific experiment or task] -- because [rationale]

Prioritize by: expected impact * probability of success.

### Step 7: Update Findings

Append a dated synthesis to `findings.md`:

```markdown
## Week of YYYY-MM-DD

### Summary
[2-3 sentences on the week's progress]

### Key Findings
- [finding 1]
- [finding 2]

### Metric Progress
- Baseline: X.XXXXXX
- Last week best: X.XXXXXX
- This week best: X.XXXXXX

### Direction
[on track / stalled / pivot needed / ready to write]

### Next Week
1. [plan item 1]
2. [plan item 2]
3. [plan item 3]
```

---

## Output Format

Present the retrospective as a conversation, not a form. Speak as a PI
who is thinking out loud about the research. Be honest about setbacks and
genuine about progress. End with clear, actionable next steps.

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

