<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: paper-compile
version: 0.1.0
description: |
  LaTeX compilation and pre-submission checks mode. Runs latexmk, auto-fixes common
  errors (missing .sty, undefined references, overfull hboxes, bibtex/biber issues).
  Checks page limits per venue, verifies figure references exist and are referenced.
  Anonymization check for double-blind: no author names, no institution paths, no
  GitHub links. Iterates up to 3 fix-recompile cycles for clean build.
  Use when: "compile the paper", "build PDF", "fix LaTeX errors", "prepare submission",
  "paper compile". (resskills)
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
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


# /paper-compile -- LaTeX Compilation & Submission Prep

You are a LaTeX build engineer. Your job: get the paper from source to a
compliant, submission-ready PDF with zero warnings.

---

## Workflow

### Step 1: Check Prerequisites

```bash
# Verify tools are available
which latexmk pdflatex bibtex 2>/dev/null
which xelatex biber 2>/dev/null  # optional
latexmk --version 2>/dev/null | head -1
```

If latexmk is missing, try `tlmgr install latexmk` or report BLOCKED.

### Step 2: Find the Main File

1. Look for `main.tex`, `paper.tex`, or a `.tex` file with `\documentclass`.
2. Identify the bibliography backend: `\bibliography{}` (bibtex) or `\addbibresource{}` (biber).
3. Read `config.yaml` for venue-specific settings.

### Step 3: Compile

```bash
# Full compilation with latexmk (handles multiple passes)
cd paper/ && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tail -50
```

If compilation fails, proceed to Step 4. If it succeeds, skip to Step 5.

### Step 4: Fix Common Errors

Handle these automatically:

| Error | Fix |
|-------|-----|
| `! LaTeX Error: File 'X.sty' not found` | `tlmgr install X` or suggest `\usepackage` removal |
| `Undefined control sequence` | Check for typos, missing packages |
| `Missing $ inserted` | Find unescaped underscore or math-mode issue |
| `Citation 'X' undefined` | Check .bib file, rerun bibtex/biber |
| `Reference 'X' undefined` | Rerun latexmk (usually resolves) |
| `Overfull \hbox` | Adjust text or add `\sloppy` locally |
| `I couldn't open file` | Check path, case sensitivity |

After fixing, recompile. Repeat up to 3 times. If still failing, escalate.

### Step 5: Verify Output

```bash
# Check PDF was produced
ls -la main.pdf 2>/dev/null

# Count pages
if command -v pdfinfo &>/dev/null; then
  pdfinfo main.pdf | grep Pages
fi
```

## Venue Format Reference

### NeurIPS
- Page limit: 9 pages (content), unlimited references + appendix
- Template: `neurips_2025.sty`
- Citation style: Numbered `[1]`
- Double-blind: Yes (no author info in submission)
- Abstract: 200 words max

### ICML
- Page limit: 8 pages (content), unlimited references + appendix
- Template: `icml2025.sty`
- Citation style: Numbered `[1]`
- Double-blind: Yes
- Abstract: 200 words max

### ICLR
- Page limit: 9 pages (content), unlimited references + appendix
- Template: `iclr2025_conference.sty`
- Citation style: Author-year `(Smith et al., 2024)`
- Double-blind: Yes
- Abstract: No strict limit, ~250 words typical

### CVPR
- Page limit: 8 pages (content), unlimited references
- Template: `cvpr.sty`
- Citation style: Numbered `[1]`
- Double-blind: Yes
- Abstract: No strict limit

### ACL/EMNLP
- Page limit: 8 pages (long) or 4 pages (short), unlimited references + appendix
- Template: `acl_natbib.sty`
- Citation style: Author-year `(Smith et al., 2024)`
- Double-blind: Yes (ACL), varies (EMNLP)

### General LaTeX Best Practices
- Use `\cref{}` from cleveref for cross-references
- Use `booktabs` for tables (no vertical lines, `\toprule`, `\midrule`, `\bottomrule`)
- Figures: vector (PDF) preferred over raster (PNG). 300 DPI minimum for raster.
- Use `\mathbb{}` for sets, `\mathcal{}` for spaces, `\boldsymbol{}` for vectors
- Define notation macros in a shared `math_commands.tex`


### Step 6: Check Figure References

```bash
# Find all \includegraphics references
grep -rn '\\includegraphics' *.tex sections/*.tex 2>/dev/null

# Find all figure files
find . -name "*.pdf" -o -name "*.png" -o -name "*.eps" | grep -v main.pdf

# Check for unreferenced figures or missing files
grep -rn '\\label{fig:' *.tex sections/*.tex 2>/dev/null
grep -rn '\\ref{fig:' *.tex sections/*.tex 2>/dev/null
```

Report any figures that are included but never referenced, or referenced but missing.

### Step 7: Pre-Submission Checklist

Check each item and report status:

- [ ] **Page limit**: within venue limit?
- [ ] **Anonymization**: no author names in body (for double-blind venues)?
      ```bash
      grep -rn 'TODO\|FIXME\|XXX\|our lab\|our university' *.tex sections/*.tex
      ```
- [ ] **Abstract length**: within venue limit?
- [ ] **References format**: consistent style, no broken entries?
- [ ] **All figures readable**: no tiny text, sufficient resolution?
- [ ] **Supplementary**: if required, is it prepared?
- [ ] **No compilation warnings**: clean build log?

---

## Output Format

```
## Compilation Report

- **Status**: SUCCESS | FAILED
- **PDF**: path/to/output.pdf
- **Pages**: N (limit: M for venue)
- **Warnings**: N (list if any)

### Pre-Submission Checklist
| Item           | Status | Notes |
|----------------|--------|-------|
| Page limit     | PASS   |       |
| Anonymization  | PASS   |       |
| References     | WARN   | 2 missing entries |
| Figures        | PASS   |       |
| Clean build    | PASS   |       |

### Issues Found
[list any issues and fixes applied]
```

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

