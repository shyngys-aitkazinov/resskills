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

# Learnings (per-project, if any)
_LEARN="${HOME}/.resskills/projects/${_SLUG}/learnings.md"
[ -f "$_LEARN" ] && echo "LEARNINGS: $_LEARN ($(wc -l < "$_LEARN" 2>/dev/null | tr -d ' ') lines)"
```

Use the context above to understand the project state. If a config file exists, use its
values. If not, infer what you need from the project files, or ask the user if ambiguous.
Do not assume defaults -- understand the situation and act accordingly.


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

