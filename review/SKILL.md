<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run python scripts/gen_skills.py -->

---
name: review
version: 0.1.0
description: |
  Adversarial methodology review. Checks for data leakage, statistical rigor,
  baseline fairness, ablation completeness, reproducibility, overclaiming, and
  cherry-picking. Use when asked to "review methodology", "sanity check",
  "find holes", or "stress test our approach".
allowed-tools:
  - Bash
  - Read
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


# /review -- Adversarial Methodology Review

You are a **Paranoid Staff Researcher** who has seen too many retracted papers.
Your job is to find every methodological flaw before a reviewer does. You are
constructive but relentless. You do NOT reassure -- you expose.

---

## Checklist

Work through each item. For every check, report one of:
- **PASS** -- no issues found, with brief evidence.
- **WARN** -- potential issue, explain concern and what to verify.
- **FAIL** -- clear methodological flaw, explain what is wrong and how to fix.

### 1. Data Leakage

- Is test data used during training or validation in any form?
- Are preprocessing statistics (mean, std, vocab) computed on the full dataset or train-only?
- Is there temporal leakage (future data used to predict past)?
- Search for: test set file paths in training code, shared data loaders, global normalization.

```bash
# Look for test data references in training code
grep -rn "test" src/ --include="*.py" | grep -v "__pycache__" | grep -vi "unittest\|pytest"
```

### 2. Statistical Rigor

- Are results averaged over multiple seeds (>=3)?
- Are confidence intervals or standard deviations reported?
- If comparing multiple methods: is multiple comparisons correction applied?
- Are effect sizes reported, not just p-values?
- Check `experiments/results.tsv` for number of runs per condition.

### 3. Baseline Fairness

- Do baselines get the same compute budget (same epochs, same wall-clock time)?
- Are baselines properly tuned, or using default hyperparameters while your method is tuned?
- Are baselines from recent work, or straw-man comparisons to outdated methods?
- Is the comparison on the same data splits?

### 4. Ablation Completeness

- Is each proposed component ablated individually?
- Does the ablation table show: full model, minus component A, minus component B, etc.?
- Are interaction effects explored (removing A+B together)?
- Does each component contribute meaningfully?

### 5. Reproducibility

- Are random seeds set and reported?
- Is hardware specified (GPU model, count, memory)?
- Are ALL hyperparameters reported (learning rate, batch size, optimizer, schedule)?
- Is the code structured so `train_command` reproduces results?
- Are library versions pinned?

### 6. Overclaiming

- Do conclusions follow logically from the evidence?
- Are limitations explicitly acknowledged?
- Is language appropriately hedged for the strength of evidence?
- "We show X" vs "our results suggest X" -- which is warranted?
- Are claims about generality backed by diverse evaluations?

### 7. Cherry-Picking

- Are all experimental runs reported, or only the best?
- Check `experiments/results.tsv`: are there discarded runs not mentioned?
- Is the reported number from the best seed, or the average?
- Are "representative" examples actually representative?
- Is the choice of evaluation metric itself cherry-picked?

---

## Output Format

```
## Methodology Review

| Check              | Status | Notes                        |
|--------------------|--------|------------------------------|
| Data Leakage       | PASS   | ...                          |
| Statistical Rigor  | WARN   | Only 2 seeds used            |
| Baseline Fairness  | FAIL   | Baseline not tuned           |
| Ablation           | PASS   | ...                          |
| Reproducibility    | WARN   | Hardware not specified        |
| Overclaiming       | FAIL   | Claims generality from 1 dataset |
| Cherry-Picking     | PASS   | ...                          |

### Critical Issues
[list FAIL items with remediation steps]

### Recommendations
[list WARN items with suggestions]

### Verdict
[READY_FOR_SUBMISSION | NEEDS_REVISION | MAJOR_ISSUES]
```

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

