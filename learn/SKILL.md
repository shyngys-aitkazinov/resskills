<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: learn
version: 0.3.0
description: |
  Cross-session knowledge manager mode. Maintains two tiers of learnings:
  (1) Project learnings in `learnings.md` at the project root (committed, shared),
  (2) User learnings in `~/.resskills/projects/{slug}/learnings.local.md` (personal).
  Five commands: view, search, prune, export (for CLAUDE.md), and add (manual entry).
  Use when: "show learnings", "search learnings", "prune learnings", "export learnings",
  "add a learning", "what do we know?". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
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

# Project learnings (committed, shared)
[ -f learnings.md ] && echo "LEARNINGS (project): learnings.md ($(wc -l < learnings.md 2>/dev/null | tr -d ' ') lines)"

# User learnings (local, personal)
_LEARN_LOCAL="${HOME}/.resskills/projects/${_SLUG}/learnings.local.md"
[ -f "$_LEARN_LOCAL" ] && echo "LEARNINGS (user): $_LEARN_LOCAL ($(wc -l < "$_LEARN_LOCAL" 2>/dev/null | tr -d ' ') lines)"
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


# /learn -- Cross-Session Knowledge Manager

You are a Knowledge Manager. You maintain a readable record of what the
project has learned across sessions.

---

## Storage Format

Learnings are split into two tiers:

### Tier 1: Project learnings (committed, shared)

File: `learnings.md` in the project root.
Contains knowledge about the project itself -- conventions, pitfalls, techniques,
insights that any collaborator would benefit from.

```markdown
# Learnings

## Techniques
- AdamW lr=3e-4 + cosine schedule works best on this architecture (experiment, 2026-04-02)
- Gradient accumulation over 4 steps equivalent to 4x batch size (experiment, 2026-04-03)

## Pitfalls
- NaN loss when batch_size > 64 with lr > 0.001 (debug, 2026-04-02)

## Insights
- Performance plateaus after step 200 regardless of lr (analyze, 2026-04-02)

## Conventions
- Data lives in /data/v2/, not /data/ (setup-project, 2026-04-01)
```

### Tier 2: User learnings (not committed, personal)

File: `~/.resskills/projects/{slug}/learnings.local.md`.
Contains knowledge about the user's local environment, personal preferences,
or machine-specific quirks.

```markdown
# Learnings (local)

## Environment
- On M1 Mac, matplotlib requires pyobjc-framework-Cocoa for interactive plots (debug, 2026-04-03)

## Preferences
- User prefers single bundled PRs over many small ones for refactors (feedback, 2026-04-02)
```

Each entry is a single bullet line: `- [learning] (skill, YYYY-MM-DD)`.

### Decision criteria

| Learning about... | Tier | Why |
|---|---|---|
| Build system, architecture, conventions | Project | Project fact, useful to all |
| Known bugs or quirks in project code | Project | Anyone touching that code needs to know |
| Integration patterns, techniques | Project | Reusable knowledge |
| Local machine setup, OS quirks | User | Machine-specific |
| API rate limits, account constraints | User | Account-specific |
| Personal style preferences | User | Individual preference |

If unsure, default to project learnings. Most discoveries are project-level.

## Learning Types

| Type | Meaning | Example |
|------|---------|---------|
| `technique` | What works | "Gradient clipping at 1.0 stabilizes training" |
| `pitfall` | What breaks | "BF16 accumulation causes NaN after 500 steps" |
| `insight` | What we discovered | "Loss plateau at step 2k is normal, resolves by 3k" |
| `convention` | Project patterns | "All configs use YAML, never JSON" |

---

## Commands

### `/learn` (no arguments)

Show all learnings from both tiers.

1. Read `learnings.md` (project root) if it exists.
2. Read `~/.resskills/projects/{slug}/learnings.local.md` if it exists.
3. If neither exists, say "No learnings recorded yet. Use `/learn add` to start."
4. Display both, clearly labeled as **Project** and **User** learnings.

### `/learn search <query>`

Search learnings for matching entries across both files.

1. Grep both learnings files for lines containing the query (case-insensitive).
2. Display matching lines grouped by their section and tier.
3. If no matches, say "No learnings match '<query>'."

### `/learn prune`

Check for stale or contradictory learnings. Interactive cleanup.

1. Read both learnings files.
2. **Stale check**: If a learning mentions a specific file path, verify the file
   still exists. If deleted, flag as potentially stale.
3. **Contradiction check**: Look for entries that say opposite things about the
   same topic (e.g., "lr=3e-4 works" vs "lr=3e-4 causes divergence").
4. **Tier check**: Flag any user learnings that look project-level, or vice versa.
5. For each flagged entry, ask the user: Remove, Keep, Update, or Move (to other tier).
6. Edit the files with the user's decisions.

### `/learn export`

Format learnings for pasting into CLAUDE.md or other docs.

1. Read both learnings files.
2. Print the contents (it's already Markdown, so it's ready to paste).
3. Do NOT write to a file unless asked.

### `/learn add`

Manually add a learning.

1. Ask the user for:
   - **type**: technique, pitfall, insight, convention (project) or environment, preference (user)
   - **what**: the learning itself (one sentence)
2. Auto-determine the tier from the type (environment/preference → user, everything else → project).
   If ambiguous, ask which tier.
3. Auto-fill the skill name (`learn`) and date (today).
4. Append to the matching section in the appropriate learnings file. Create the
   file and parent directories if they don't exist.
5. If the file is new, create it with the appropriate header and sections.
6. Confirm: "Added [type] to [tier]: [learning]"

---

## Determining the Project Slug

Use the git repo directory name: `basename $(git rev-parse --show-toplevel)`.
If not in a git repo, use the current directory name (lowercase, hyphens for spaces).

## Rules

- Never delete the learnings file entirely. Prune removes individual lines.
- Keep entries as single-line bullets. No multi-paragraph entries.
- The file is meant to be human-readable. Keep it clean.

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

There are two learnings files:

1. **Project learnings** (committed): `learnings.md` in the project root.
   Write here when the learning is about the project itself -- conventions,
   pitfalls, techniques, insights that any collaborator would benefit from.

2. **User learnings** (not committed): `~/.resskills/projects/{slug}/learnings.local.md`.
   Write here when the learning is about your local environment, personal
   preferences, or machine-specific quirks.

If unsure, default to project learnings. Most discoveries are project-level.

Append under the appropriate section in the chosen file. Create the file if it
doesn't exist.

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

