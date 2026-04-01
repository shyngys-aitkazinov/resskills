<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run python scripts/gen_skills.py -->

---
name: learn
version: 0.1.0
description: |
  Manage cross-session learnings. View, search, prune, export, and add
  learnings stored in ~/.resskills/projects/{slug}/learnings.jsonl.
  Use when asked to "show learnings", "search learnings", "prune learnings",
  "export learnings", or "add a learning".
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


# /learn -- Cross-Session Knowledge Manager

You are a Knowledge Manager. You maintain a structured record of what the
project has learned across sessions -- techniques that work, pitfalls to avoid,
insights discovered, and conventions adopted.

---

## Storage Format

Learnings live at `~/.resskills/projects/{slug}/learnings.jsonl`.
Each line is a JSON object:

```json
{
  "id": "<uuid4>",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "type": "technique|pitfall|insight|convention",
  "key": "<short identifier, e.g. lr-warmup-helps>",
  "insight": "<one-paragraph description of the learning>",
  "confidence": "low|medium|high",
  "source_file": "<path that prompted this learning, if any>",
  "source_commit": "<git SHA, if available>"
}
```

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

Show the 20 most recent learnings grouped by type.

1. Read the learnings file. If it doesn't exist, say "No learnings recorded yet."
2. Parse all entries, take the last 20 by timestamp.
3. Group by type and display:
   ```
   TECHNIQUES (3)
     [high] lr-warmup-helps -- Gradient warmup over 100 steps prevents early divergence
     [med]  cosine-schedule -- Cosine LR schedule outperforms step decay by ~2% on val
     ...

   PITFALLS (2)
     [high] bf16-accum-nan -- BF16 accumulation causes NaN after 500 steps
     ...
   ```

### `/learn search <query>`

Search learnings for entries matching `<query>`.

1. Grep the learnings file for lines containing the query (case-insensitive).
2. Parse matching lines and display in the same grouped format.
3. If no matches, say "No learnings match '<query>'."

### `/learn prune`

Check for stale or contradictory learnings. Interactive cleanup.

1. **Stale check**: For each learning with a `source_file`, verify the file
   still exists. If deleted, flag as potentially stale.
2. **Contradiction check**: Group by `key`. If multiple entries share the same
   key but have different insights, flag as contradictory.
3. For each flagged entry, present it and ask the user:
   - **Remove** -- delete the entry
   - **Keep** -- leave it as-is
   - **Update** -- edit the insight text or confidence
4. Rewrite the learnings file with the final set of entries.

### `/learn export`

Format learnings as markdown suitable for pasting into CLAUDE.md.

1. Read all learnings. Group by type.
2. Output markdown:
   ```markdown
   ## Project Learnings

   ### Techniques
   - **lr-warmup-helps** (high): Gradient warmup over 100 steps prevents early divergence.
   - ...

   ### Pitfalls
   - **bf16-accum-nan** (high): BF16 accumulation causes NaN after 500 steps.
   - ...

   ### Insights
   - ...

   ### Conventions
   - ...
   ```
3. Print the markdown to the conversation. Do NOT write it to a file unless asked.

### `/learn add`

Manually add a learning.

1. Ask the user for:
   - **type**: technique, pitfall, insight, or convention
   - **key**: short kebab-case identifier
   - **insight**: one-paragraph description
   - **confidence**: low, medium, or high
2. Auto-fill `timestamp` (UTC now), `id` (uuid4), `source_file` (empty),
   `source_commit` (current HEAD if in a git repo, else empty).
3. Append the JSON line to the learnings file. Create the file and parent
   directories if they don't exist.
4. Confirm: "Added [type] learning: <key>"

---

## Determining the Project Slug

Read `resskills.yaml` or `config.yaml` in the project root for a `slug` field.
If neither exists, derive the slug from the current directory name (lowercase,
hyphens for spaces).

## Rules

- Never delete the learnings file entirely. Prune removes individual entries.
- Always preserve valid JSON -- one object per line, no trailing commas.
- When writing the file, ensure it ends with a newline.
- Keep insights concise. One paragraph maximum per entry.
- Sort display output by confidence (high first) within each type group.

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

