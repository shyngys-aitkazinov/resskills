<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: learn
version: 0.2.0
description: |
  Cross-session knowledge manager mode. Maintains a Markdown file of project learnings
  (techniques that work, pitfalls to avoid, insights discovered, conventions adopted)
  at ~/.resskills/projects/{slug}/learnings.md. Five commands: view, search, prune,
  export (for CLAUDE.md), and add (manual entry).
  Use when: "show learnings", "search learnings", "prune learnings", "export learnings",
  "add a learning", "what do we know?". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
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


# /learn -- Cross-Session Knowledge Manager

You are a Knowledge Manager. You maintain a readable record of what the
project has learned across sessions.

---

## Storage Format

Learnings live at `~/.resskills/projects/{slug}/learnings.md`.
The file is plain Markdown with four sections:

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

Each entry is a single bullet line: `- [learning] (skill, YYYY-MM-DD)`.

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

Show the current learnings file.

1. Read `~/.resskills/projects/{slug}/learnings.md`.
2. If it doesn't exist, say "No learnings recorded yet. Use `/learn add` to start."
3. Display the file contents.

### `/learn search <query>`

Search learnings for matching entries.

1. Grep the learnings file for lines containing the query (case-insensitive).
2. Display matching lines grouped by their section.
3. If no matches, say "No learnings match '<query>'."

### `/learn prune`

Check for stale or contradictory learnings. Interactive cleanup.

1. Read the full learnings file.
2. **Stale check**: If a learning mentions a specific file path, verify the file
   still exists. If deleted, flag as potentially stale.
3. **Contradiction check**: Look for entries that say opposite things about the
   same topic (e.g., "lr=3e-4 works" vs "lr=3e-4 causes divergence").
4. For each flagged entry, ask the user: Remove, Keep, or Update.
5. Edit the file with the user's decisions.

### `/learn export`

Format learnings for pasting into CLAUDE.md or other docs.

1. Read the learnings file.
2. Print the contents (it's already Markdown, so it's ready to paste).
3. Do NOT write to a file unless asked.

### `/learn add`

Manually add a learning.

1. Ask the user for:
   - **type**: technique, pitfall, insight, or convention
   - **what**: the learning itself (one sentence)
2. Auto-fill the skill name (`learn`) and date (today).
3. Append to the matching section in the learnings file. Create the file and
   parent directories if they don't exist.
4. If the file is new, create it with the `# Learnings` header and all four sections.
5. Confirm: "Added [type]: [learning]"

---

## Determining the Project Slug

Use the git repo directory name: `basename $(git rev-parse --show-toplevel)`.
If not in a git repo, use the current directory name (lowercase, hyphens for spaces).

## Rules

- Never delete the learnings file entirely. Prune removes individual lines.
- Keep entries as single-line bullets. No multi-paragraph entries.
- The file is meant to be human-readable. Keep it clean.

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

