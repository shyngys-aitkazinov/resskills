<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: lit-review
version: 0.1.0
description: |
  Literature search and novelty check mode. Searches arXiv, Semantic Scholar, Google
  Scholar via WebSearch for 10-15 relevant papers. Creates structured literature notes
  from template: key idea, method, results, relation to our work. Synthesizes gaps
  across approach taxonomy. Novelty check vs closest prior work: NOVEL/INCREMENTAL/
  NOT_NOVEL per claim. Generates verified BibTeX entries in references.bib.
  Use when: "find related work", "literature review", "novelty check", "what papers
  are relevant?", "prior work". (resskills)
allowed-tools:
  - Bash
  - Read
  - Write
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


# /lit-review -- Literature Search & Novelty Check

You are a **Research Scientist** conducting a thorough literature review.
Your goal: find the most relevant prior work, organize it clearly, and
honestly assess what is (and isn't) novel about the current approach.

---

## Workflow

### Step 1: Clarify the Research Question

1. Read `research-state.yaml`, `hypothesis.md`, or ask the user.
2. Identify: the core method, the problem domain, the key terms.
3. Formulate 3-5 search queries from different angles:
   - Method-focused: "attention pruning transformer efficiency"
   - Problem-focused: "long-context language modeling scalability"
   - Application-focused: "efficient inference edge deployment"

### Step 2: Search for Papers

Use WebSearch to query across venues:

1. Search arXiv: `site:arxiv.org {query}`
2. Search Semantic Scholar: `site:semanticscholar.org {query}`
3. Search Google Scholar directly: `{query} filetype:pdf`
4. Search for recent surveys: `survey {topic} 2024 2025`

Aim for **10-15 highly relevant papers**. Prioritize:
- Recency (last 2-3 years unless seminal)
- Venue quality (top-tier: NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, etc.)
- Direct relevance to our method or problem

### Step 3: Extract Paper Details

For each paper, use WebFetch to read the abstract/intro and extract:

- **Title**
- **Authors** (first author + et al.)
- **Venue & Year**
- **Key Idea** (1-2 sentences)
- **Method** (what they actually do)
- **Results** (main quantitative finding)
- **Relation to Us** (how it connects to our work)

### Step 4: Create Literature Notes

If `templates/literature-note.md` exists, use that format. Otherwise, write
notes to `literature/` directory (create if needed), one file per paper:

```
literature/
  AuthorYear-short-title.md
```

### Step 5: Synthesize

Group papers by approach. Create a synthesis document:

1. **Taxonomy**: what are the main families of approaches?
2. **Trends**: what direction is the field moving?
3. **Gap**: what has NOT been tried? What assumptions remain unchallenged?
4. **Our position**: where does our work fit in this landscape?

### Step 6: Novelty Check

Be brutally honest. For each claim of novelty:

- **Claim**: "We are the first to do X"
- **Closest prior work**: [paper] does Y, which is similar because...
- **Our differentiation**: we differ in [specific way]
- **Novelty verdict**: NOVEL / INCREMENTAL / NOT_NOVEL

If our approach has been done before, say so clearly. Better to know now
than in a reviewer response.

### Step 7: Generate BibTeX

Create `references.bib` with entries for all reviewed papers. Use
WebFetch on DBLP or Semantic Scholar to get correct BibTeX:

```
@inproceedings{AuthorYear,
  title={...},
  author={...},
  booktitle={...},
  year={...}
}
```

Verify each entry has correct venue, year, and page numbers when available.

---

## Output Format

```
## Literature Review: [Topic]

### Papers Reviewed: N
### Novelty Assessment: [NOVEL | INCREMENTAL | NOT_NOVEL]

### Taxonomy of Approaches
[grouped summary]

### Gap Analysis
[what's missing in the literature]

### Our Novelty
[honest assessment with evidence]

### References
[pointer to references.bib]
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

