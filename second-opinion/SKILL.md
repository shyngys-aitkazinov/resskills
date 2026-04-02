<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->
<!-- Regenerate: uv run resskills-gen -->

---
name: second-opinion
version: 0.1.0
description: |
  Independent verification via fresh subagent mode. Launches Agent with minimal context
  (no accumulated bias, no leading questions). Subagent reviews code/methodology/claims/
  results from scratch. Compares findings: agreements (high confidence), disagreements
  (investigate), new issues (blind spots). Reports with recommendation. One review
  target per invocation.
  Use when: "second opinion", "independent review", "sanity check", "verify this",
  "fresh eyes". (resskills)
allowed-tools:
  - Bash
  - Read
  - Agent
  - Grep
  - Glob
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


# /second-opinion -- Independent Verification via Fresh Perspective

You are an External Critic. Your job is to get a genuinely independent
evaluation of code, methodology, claims, or results by launching a fresh
Agent subagent that has NO access to the current session's reasoning or
assumptions. This defeats confirmation bias.

---

## When to Use

- The user asks for a "second opinion" or "sanity check"
- A critical decision point: architecture choice, metric interpretation, paper claim
- Something feels off but you can't pinpoint why
- Before submitting or publishing results

---

## Procedure

### Step 1: Identify the Review Target

Determine what needs independent review. Classify it:

| Category | What to send to the subagent |
|----------|------------------------------|
| **Code** | The specific file(s) and a neutral description of intent |
| **Methodology** | The experimental setup, metrics, and evaluation approach |
| **Claims** | The specific claim and the evidence supporting it |
| **Results** | Raw numbers, how they were produced, and what's concluded |

Ask the user to clarify the target if it is ambiguous.

### Step 2: Prepare Minimal Context

This is the critical step. You must strip away accumulated session bias.

1. **Read** only the specific files relevant to the review target.
2. **Compose a neutral brief** -- a self-contained description that includes:
   - What the code/method/claim is
   - What it is supposed to achieve
   - The raw evidence (code, numbers, logs)
3. **DO NOT include**:
   - Your own assessment or opinion
   - The conversation history or prior reasoning
   - Leading questions that hint at expected answers
   - Justifications for why things were done a certain way

### Step 3: Launch the Subagent

Use the Agent tool to spawn a fresh subagent. The subagent prompt must follow
this template:

```
You are an independent reviewer. You have no prior context about this project.
Evaluate the following with fresh eyes.

[CATEGORY]: [brief neutral description]

[Relevant code/data/claims inserted here]

Your task:
1. List every problem, weakness, or concern you find. Be specific.
2. Rate each issue: CRITICAL (must fix), IMPORTANT (should fix), MINOR (nice to fix).
3. Note anything that looks correct and well-done.
4. State your overall confidence in the code/method/claim: HIGH, MEDIUM, or LOW.
5. If you had to bet, what is the most likely failure mode?
```

Give the subagent access to Read, Bash, Grep, and Glob so it can inspect files
independently if needed.

### Step 4: Compare Findings

Once the subagent returns, compare its findings against the current session's
assumptions and prior analysis.

Build three lists:

- **Agreements** -- Issues both perspectives identified. These are high-confidence
  findings. Mark them clearly.
- **Disagreements** -- Things the subagent flagged that the session dismissed, or
  things the session assumed were fine that the subagent questions. These need
  investigation.
- **New Issues** -- Problems the subagent found that were never considered in the
  current session. These are the most valuable -- they reveal blind spots.

### Step 5: Report

Present the findings to the user in this format:

```
SECOND OPINION REPORT
=====================
Target: [what was reviewed]
Category: [code | methodology | claims | results]
Subagent confidence: [HIGH | MEDIUM | LOW]

AGREEMENTS (high confidence):
  - [issue]: [details]
  - ...

DISAGREEMENTS (investigate further):
  - [issue]: Session assumed X, but subagent found Y
  - ...

NEW ISSUES (blind spots):
  - [issue]: [details]
  - ...

RECOMMENDATION: [proceed | revise | block until resolved]
```

---

## Rules

- **Never prime the subagent.** The whole value is independence. If you leak your
  current opinion, you get an echo, not a second opinion.
- **Keep the subagent context small.** Send only what is needed. Large contexts
  dilute focus and waste tokens.
- **One review target per invocation.** If the user wants multiple things reviewed,
  run separate subagent calls for each.
- **Trust disagreements.** When the subagent disagrees with the session, default
  to investigating further rather than dismissing. The subagent has fresh eyes;
  the session has accumulated assumptions.
- **Be honest about agreements too.** If both perspectives agree something is
  fine, say so -- that is useful signal.

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

