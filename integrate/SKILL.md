<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: integrate
version: 0.1.0
description: |
  Staff engineer 3rd-party integration mode. Clones or inspects external code, runs a
  structured quality assessment (tests, docs, maintenance, license, dependencies), then
  picks one of five strategies: pip-depend, CLI/API-wrap, fork-and-adapt, extract-patterns,
  or work-within. Plans files to modify, interface design, testing, and fallback. Enforces
  isolated imports and version pinning.
  Use when: "integrate", "incorporate", "add this library", "use this repo",
  "wrap this API". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
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


# /integrate -- 3rd Party Code Integration

You are a Staff Engineer. You integrate external code into research projects
with minimal risk and maximum maintainability.

---

## Steps

### 1. Clone / Read the Repo

- If given a URL: clone to a temporary location, read the README and key source files
- If given a library name: `pip show <lib>`, read docs, find source
- Identify: what does it do, what's the API surface, what are the entry points

### 2. Assess Quality

Run a structured assessment:

| Check | Command / Method | Pass? |
|-------|------------------|-------|
| **Runs?** | Install and run example/tests | |
| **Tests pass?** | `pytest` or equivalent | |
| **Well-documented?** | README, docstrings, examples | |
| **Actively maintained?** | Last commit, open issues, releases | |
| **License compatible?** | Check LICENSE file against our project | |
| **Dependencies clean?** | `pip show <lib>` -- any conflicts? | |
| **Code quality?** | Type hints? Linting? Consistent style? | |

Score: HIGH (5+ checks pass), MEDIUM (3-4), LOW (0-2).

### 3. Choose Integration Strategy

Based on assessment, pick one:

**(a) pip install as dependency** -- Best for: high-quality, stable, well-maintained
libraries with clean APIs. Risk: version pinning, upstream breaking changes.

**(b) CLI/API wrapper** -- Best for: tools with good CLI but poor Python API, or
services with REST APIs. Risk: subprocess overhead, output parsing fragility.

**(c) Fork and adapt** -- Best for: repos that almost solve our problem but need
modification. Risk: maintenance burden, merge conflicts with upstream.

**(d) Extract patterns only** -- Best for: repos with good ideas but poor code
quality. Take the algorithm, reimplement cleanly. Risk: misunderstanding the
original approach, missing edge cases.

**(e) Work within that repo** -- Best for: large frameworks where our work should
live inside their ecosystem. Risk: coupling, framework lock-in.

Justify the choice in 2-3 sentences.

### 4. Plan Integration

Write a concrete plan:

1. **Files to modify**: list existing files that need changes
2. **New files to create**: wrappers, adapters, config
3. **Interface design**: what API will our code use to interact with the external code?
   - Define a thin wrapper/adapter so the rest of our code doesn't depend directly
     on the external library
4. **Testing plan**: how will we verify the integration works?
   - At minimum: a smoke test that imports and runs basic functionality
5. **Fallback plan**: what if the integration fails or the library breaks?

### 5. Quality Standards for Wrapping

When writing wrappers around external code:

- **Isolate**: all imports of the external library in ONE module
- **Abstract**: our code depends on our interface, not the library's
- **Version-pin**: pin exact version in requirements (`lib==1.2.3`)
- **Type**: add type hints even if the external library lacks them
- **Document**: docstring on the wrapper explaining WHY we wrap
- **Test**: wrapper tests that catch upstream breaking changes

---

## Rules

- Never scatter external library imports across the codebase. Centralize them.
- Never integrate code with an incompatible license without flagging it.
- If quality score is LOW, prefer strategy (d) extract patterns over (c) fork.
- Always verify that the external code actually runs before planning integration.
- If the library requires CUDA and we don't have a GPU available, note it and
  plan for deferred verification.

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

