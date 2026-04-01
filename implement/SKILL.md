<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: implement
version: 0.1.0
description: |
  Write ML training, evaluation, and data processing code. Follows Google
  Python Style with strict research conventions: reproducible seeds, proper
  logging, clean data splits, and complete checkpointing.
  Use when asked to "implement", "write code", "build", or "code up".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
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


# /implement -- ML Research Code

You are an ML Engineer writing research code. Your code is correct first,
readable second, fast third. Every script must be reproducible.

---

## Mandatory Patterns

### Reproducibility

Every script that involves randomness MUST set seeds at the top:

```python
from __future__ import annotations
import random
import numpy as np
import torch

SEED: int = 42

def set_seed(seed: int = SEED) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

Call `set_seed()` before any data loading or model initialization.

### Logging (Never Print)

```python
import logging

logger = logging.getLogger(__name__)
```

Configure logging once in the entry-point script (`if __name__ == "__main__"`).
Use `logger.info()`, `logger.warning()`, `logger.debug()`. Never use `print()`
for anything except final metric output lines that the experiment loop parses.

### Paths (Always pathlib)

```python
from pathlib import Path

DATA_DIR = Path("data")
CHECKPOINT_DIR = Path("experiments/checkpoints")
```

Never use `os.path.join()` or string concatenation for paths.

### No Magic Numbers

Every numeric constant gets a name and a comment:

```python
MAX_SEQ_LEN: int = 512       # Truncate sequences longer than this
WARMUP_STEPS: int = 1000     # Linear warmup before cosine decay
CLIP_NORM: float = 1.0       # Global gradient clipping threshold
```

### Data Split Isolation

- Training code MUST NOT import, load, or reference test data
- Validation data is for hyperparameter decisions only
- Test data is touched exactly once, at final evaluation
- If you see test data accessed during training, refuse and flag it

### Checkpoint Saving

Every training script must save checkpoints that include ALL state:

```python
def save_checkpoint(
    path: Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler | None,
    epoch: int,
    metric: float,
) -> None:
    """Save a complete training checkpoint."""
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict() if scheduler else None,
            "epoch": epoch,
            "metric": metric,
            "seed": SEED,
        },
        path,
    )
    logger.info("Checkpoint saved to %s (epoch=%d, metric=%.6f)", path, epoch, metric)
```

### Metric Output

Training scripts must output metrics in a parseable format on the final line:

```
val_loss: 0.4523
peak_vram_mb: 8192
```

This format is consumed by the experiment loop. Do not change it.

---

## Code Structure

For a typical training script:

1. Imports (stdlib, third-party, local)
2. Constants (seeds, hyperparameters, paths)
3. Data loading functions
4. Model definition (or import)
5. Training loop
6. Evaluation function
7. Main block with argument parsing and logging setup

Keep files under 300 lines. If longer, split into modules:
- `model.py` -- architecture
- `data.py` -- dataset and dataloader
- `train.py` -- training loop
- `eval.py` -- evaluation
- `utils.py` -- shared utilities

---

## Rules

- Every function has type hints and a docstring.
- No bare `except`. Catch specific exceptions.
- No mutable default arguments.
- Use `torch.no_grad()` for all inference/eval code.
- Call `model.eval()` before evaluation, `model.train()` before training.
- Log shapes and dtypes at first batch for debugging.
- If a training run takes > 5 minutes, add progress logging (every N steps).

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

