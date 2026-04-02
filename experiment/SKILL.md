<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: experiment
version: 0.1.0
description: |
  Autonomous ML experiment runner mode. Modify-train-evaluate loop: edits code, runs
  training, keeps improvements, git-reverts failures. Git history as experiment memory.
  Seven-phase cycle (review, ideate, modify, commit, run, guard, decide) with outer-loop
  reflection every 5-10 experiments. Runs indefinitely at ~12 experiments/hour.
  Use when: "run experiments", "start the loop", "overnight run", "try things
  autonomously", "experiment loop". (resskills)
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
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


## Python Standards (Google Style)

All Python code should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
Key rules condensed below. Formatting and import sorting are enforced by `ruff`, not manually.

### Tooling (handles formatting automatically)

```bash
ruff check --fix .   # Lint + auto-fix (includes isort for imports)
ruff format .        # Format (line length 88, double quotes)
mypy .               # Type checking
```

Configuration lives in `pyproject.toml` under `[tool.ruff]` and `[tool.mypy]`.
Import ordering, grouping, and formatting are handled entirely by `ruff` with `I` (isort) rules enabled.
Do NOT manually sort imports.

### Naming (Guide section 3.16)

| Type | Convention | Example |
|------|-----------|---------|
| Packages, Modules | `lower_with_under` | `my_module.py` |
| Classes, Exceptions | `CapWords` | `MyClass`, `InputError` |
| Functions, Methods | `lower_with_under()` | `fetch_data()` |
| Constants | `CAPS_WITH_UNDER` | `MAX_EPOCHS` |
| Variables, Parameters | `lower_with_under` | `batch_size` |
| Private | prefix with `_` | `_internal_state` |

Avoid: single-char names (except `i`, `j`, `k`, `e`, `f`), dashes in module names,
names that include the type (`id_to_name_dict`). Exception names must end in `Error`.

### Type Hints (Guide section 2.21, 3.19)

- Annotate all public API function signatures (args + return type).
- Use `X | None` (not implicit optional like `a: str = None`).
- Use `from __future__ import annotations` for modern syntax.
- Prefer built-in generics (`list[int]`, `dict[str, Any]`) over `typing.List`, `typing.Dict`.
- Import type symbols directly: `from typing import Any, Sequence`.
- Spaces around `=` only when both annotation and default: `def f(a: int = 0)`.
- One parameter per line for long signatures, closing paren aligned with `def`:
  ```python
  def train_step(
      self,
      batch: dict[str, Tensor],
      lr: float = 1e-4,
  ) -> float:
      ...
  ```

### Docstrings (Guide section 3.8)

Google-style format. Summary line under 80 chars, ending with period.

```python
def fetch_rows(
    table: Table,
    keys: Sequence[bytes | str],
    require_all: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetch rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle. String keys will be UTF-8 encoded.

    Args:
        table: An open Table instance.
        keys: A sequence of strings representing the key of each row
            to fetch. String keys will be UTF-8 encoded.
        require_all: If True only rows with values set for all keys
            will be returned.

    Returns:
        A dict mapping keys to the corresponding table row data.

    Raises:
        IOError: An error occurred accessing the table.
    """
```

- Classes: docstring below class definition with `Attributes:` section.
- Overridden methods: no docstring needed if decorated with `@override`.
- `@property`: use attribute-style (`"""The path."""` not `"""Returns the path."""`).

### Error Handling (Guide section 2.4)

- No bare `except:`. Catch specific exceptions.
- Use `raise ... from e` for exception chaining.
- Do not use `assert` for validation in production code (only in tests).
- Minimize code in `try` blocks. Use `finally` for cleanup.
- Custom exceptions inherit from existing exception classes, name ends with `Error`.

### Formatting (Guide section 3.2, 3.4)

Handled by `ruff format`. Key points:
- Line length: 88 characters (configured in pyproject.toml).
- 4-space indentation, never tabs.
- No backslash line continuation. Use implicit joining in parens/brackets.
- Two blank lines between top-level definitions, one between methods.
- Trailing comma on multi-line collections.
- Use f-strings for formatting, not `+` concatenation.
- Use `logging` with `%`-placeholders, not f-strings in log calls.

### Files and Resources (Guide section 3.11)

- Always use `with` statements for files and sockets.
- For objects without context manager support: `contextlib.closing()`.

### Functions (Guide section 3.18)

- Prefer small, focused functions. Consider breaking up if exceeding ~40 lines.
- Always gate main logic: `if __name__ == "__main__": main()`.

### Research-Specific Conventions

These are not from the Google guide but are standard practice for ML research code:

- **Reproducibility:** Set random seeds at script entry point:
  ```python
  import random
  import numpy as np
  import torch

  SEED = 42

  def set_seed(seed: int = SEED) -> None:
      """Set random seeds for reproducibility."""
      random.seed(seed)
      np.random.seed(seed)
      torch.manual_seed(seed)
      if torch.cuda.is_available():
          torch.cuda.manual_seed_all(seed)
  ```
- **Logging:** Use `logging` module, never `print()` for status output.
- **Paths:** Use `pathlib.Path`, never string concatenation.
- **No magic numbers:** Define as named constants with comments.
- **Data splits:** Never access test data during training. Verify split isolation.
- **Checkpoints:** Save model, optimizer, scheduler, epoch, and metric together.


# /experiment -- Autonomous Research Loop

You are an autonomous ML researcher. You modify code, run experiments, and
keep what works. You NEVER stop to ask permission once the loop begins.

---

## Setup (first time only)

1. Read `config.yaml` (or project's `resskills.yaml`) for: `train_command`, `train_file`, `primary_metric`, `time_budget_min`, `metric_direction`
2. Read the train file and any prepare/eval files for full context
3. If `experiments/results.tsv` doesn't exist, create it with header:
   ```
   commit	val_bpb	memory_gb	status	description
   ```
4. Run baseline: execute `train_command`, record result as "baseline" with status "keep"
5. `git add experiments/results.tsv && git commit -m "experiment: baseline [metric=VALUE]"`

---

## The Loop

**LOOP FOREVER:**

### Phase 1: Review
1. Read `experiments/results.tsv` (last 20 entries)
2. Run `git log --oneline -20` to see what was tried
3. If the last kept commit has a diff, run `git diff HEAD~1` to understand what worked
4. Identify patterns: what improved the metric? what didn't? what's untried?

### Phase 2: Ideate
1. Based on patterns from Phase 1, decide what to try next
2. Prioritize: high-impact changes over incremental tweaks
3. If stuck: re-read the code, try combining previous near-misses, try more radical changes

### Phase 3: Modify
1. Edit the train file with ONE clear experimental change
2. Keep changes atomic. One idea per experiment.

### Phase 4: Commit
1. `git commit -am "experiment: [concise description of what changed]"`
2. This happens BEFORE training. If the experiment fails, we revert this commit.

### Phase 5: Run
1. Execute: `{train_command} > run.log 2>&1`
   - Redirect everything. Do NOT let output flood context.
   - Timeout: if exceeds 2x `time_budget_min`, kill and treat as crash
2. Extract results: `grep "^{primary_metric}:\|^peak_vram_mb:" run.log`
3. If grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the error.

### Phase 6: Guard (optional)
If a guard command is configured, run it. If it fails, treat as discard.

### Phase 7: Decide
- **Metric improved** (lower if `lower_is_better`, higher if `higher_is_better`):
  - Status: `keep`. The branch advances.
- **Metric equal or worse:**
  - Status: `discard`. Run `git revert HEAD --no-edit` to undo the commit.
- **Crash:**
  - If it's a trivial fix (typo, missing import): fix and re-run once.
  - If the idea is fundamentally broken: status `crash`, revert, move on.

### Phase 8: Log
Append a row to `experiments/results.tsv`:
```
{commit_hash_7char}	{metric_value}	{memory_gb}	{status}	{description}
```
Use `0.000000` for metric and `0.0` for memory on crashes.

**Do NOT commit results.tsv** -- leave it untracked so it doesn't clutter experiment diffs.

**GOTO Phase 1.**

---

## Rules

- **ONE change per experiment.** Isolate variables.
- **NEVER modify the eval/prepare file.** Only the train file.
- **NEVER stop to ask.** The user may be asleep.
- **Simplicity criterion:** Equal results + simpler code = keep. A 0.001 improvement
  that adds 20 lines of hacky code? Probably not worth it. A 0.001 improvement from
  deleting code? Definitely keep.
- **If stuck:** Re-read the code with fresh eyes. Try combining two previous near-misses.
  Try something radical. Read related papers referenced in the code for ideas.

## Output Format

After each experiment, print a one-line summary:
```
[N] metric={VALUE} status={keep|discard|crash} desc="{description}"
```

## Outer Loop (every 5-10 experiments)

Pause the inner loop briefly to reflect:
1. Review all results since last reflection
2. Cluster by type: what worked? what didn't?
3. Ask WHY -- identify mechanisms, not just correlations
4. Update `findings.md` with narrative synthesis
5. Decide direction: DEEPEN (more of what works), BROADEN (try new dimension),
   PIVOT (abandon current approach), or CONCLUDE (enough evidence to write up)

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

