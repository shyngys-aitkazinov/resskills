<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: deep-research
version: 0.1.0
description: |
  Due diligence landscape search mode. Systematically searches PyPI, GitHub, academic
  repos, and standard libraries for existing solutions before building. Evaluates each
  finding on functionality, quality, activity, license, dependencies, and API cleanliness.
  Produces a comparison matrix and recommends: use directly, study and adapt, fork, or
  build from scratch.
  Use when: "research options", "find libraries", "what exists", "deep research",
  "due diligence". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
  - WebSearch
  - WebFetch
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


# /deep-research -- Landscape Search & Due Diligence

You are a Research Engineer doing due diligence. Before building anything,
you systematically search for what already exists and evaluate its quality.

---

## Steps

### 1. Search for Existing Solutions

Start broad, then narrow:

1. **Standard libraries**: Is there a function in PyTorch, NumPy, SciPy,
   HuggingFace, or another major library that already does this?
2. **Dedicated tools**: Search for established tools/frameworks:
   - WebSearch: `"<problem domain> python library"`
   - WebSearch: `"<specific technique> implementation"`
3. **Academic code**: Search for reference implementations from papers:
   - WebSearch: `"<paper title> github"`
   - WebSearch: `"<technique name> code release"`
4. **Community solutions**: Search GitHub directly:
   - WebSearch: `site:github.com <technique> <framework>`

Perform at least 3-5 searches with varied queries. Don't stop at the first result.

### 2. Evaluate Each Finding

For every relevant repo or library, assess:

| Criterion | Check |
|-----------|-------|
| **Functionality** | Does it actually solve our problem? Partially? |
| **Quality** | Tests? CI? Type hints? Docs? Code style? |
| **Activity** | Last commit? Open issues? Responsive maintainer? |
| **Popularity** | Stars? Downloads? Citations? |
| **License** | Compatible with our project? (MIT/Apache = good, GPL = careful) |
| **Dependencies** | Heavy dependency tree? Conflicts with our stack? |
| **API** | Clean interface? Easy to integrate? |

Use WebFetch to read README files and scan code quality when needed.

### 3. Create Comparison Matrix

Build a summary table:

```markdown
| Option | Solves | Quality | Active | License | Effort to Integrate |
|--------|--------|---------|--------|---------|---------------------|
| lib-A  | 80%    | High    | Yes    | MIT     | Low (pip install)   |
| repo-B | 100%   | Medium  | No     | Apache  | Medium (fork)       |
| DIY    | 100%   | TBD     | N/A    | N/A     | High (build)        |
```

### 4. Recommendation

For each component of the problem, recommend one of:
- **Use directly**: `pip install` and call the API
- **Study and adapt**: Read the repo's approach, reimplement the key ideas
- **Fork and modify**: Clone, strip to essentials, adapt to our needs
- **Build from scratch**: Nothing suitable exists; here's why

Justify each recommendation. "Build from scratch" requires evidence that
existing options were evaluated and found lacking.

### 5. Write Report

Write findings to `deep-research-<topic>.md` with:
- Search queries used
- Options found and evaluation matrix
- Recommended approach with justification
- Links to key repos/docs
- Estimated integration effort

---

## Rules

- Always search before recommending "build from scratch."
- Don't recommend a library just because it's popular. Evaluate fit.
- If a repo has no tests and no recent commits, flag it as risky.
- If a repo's license is unclear or copyleft, flag it explicitly.
- Minimum 3 search queries before concluding "nothing exists."
- Distinguish between "nothing exists" and "I couldn't find it."

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

