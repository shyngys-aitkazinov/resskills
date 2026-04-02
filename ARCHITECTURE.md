# Architecture

This document explains **why** resskills is built the way it is and how the pieces fit together.

## The core idea

resskills gives Claude Code a set of opinionated research workflow skills. Everything is Markdown.

The key insight: constraining AI to specific research roles (PI, ML Engineer, Reviewer, Writer) with explicit responsibilities produces dramatically more consistent output than unconstrained prompting. A solo researcher gets the equivalent of a research team.

## Template system

SKILL.md files are **generated** from `.tmpl` templates. To update:

1. Edit the `.tmpl` file (e.g. `experiment/SKILL.md.tmpl`)
2. Run `uv run resskills-gen`
3. Commit both the `.tmpl` and generated `.md` files

```
blocks/*.md           (shared prose + instructions)
       |
       v
SKILL.md.tmpl         (human-written per-skill content + {{ placeholders }})
       |
       v  [uv run resskills-gen]
SKILL.md              (generated, committed, what Claude Code reads)
```

### How placeholders work

Placeholders use Jinja2 `{{ }}` syntax. The mechanism is simple text substitution:

1. `resskills-gen` reads every `.md` file in `blocks/` and builds a dictionary:
   - `blocks/preamble.md` → variable `PREAMBLE` (filename stem, uppercased, hyphens → underscores)
   - `blocks/python-standards.md` → variable `PYTHON_STANDARDS`
   - etc.
2. For each `SKILL.md.tmpl`, Jinja2 replaces `{{ PREAMBLE }}` with the **entire contents** of `blocks/preamble.md`
3. The result is written as `SKILL.md`

So `{{ PREAMBLE }}` literally means "paste `blocks/preamble.md` here." No logic, no conditionals, just text injection. The benefit: change `blocks/preamble.md` once, regenerate, all 21 skills update.

### Available placeholders

| Placeholder | Source | What it generates | Used by |
|-------------|--------|-------------------|---------|
| `{{ PREAMBLE }}` | `blocks/preamble.md` | Startup block: branch detection, config loading (metric, time budget, train command, venue), experiment count + best result, research state summary, findings line count, learnings count + recent entries | All 21 skills |
| `{{ VOICE }}` | `blocks/voice.md` | Tone rules: precise, evidence-based, no hand-waving. Anti-patterns list (banned AI words). Research-specific rules (exact numbers, comparisons, uncertainty quantification) | All 21 skills |
| `{{ PYTHON_STANDARDS }}` | `blocks/python-standards.md` | Google Python Style Guide: naming, type hints, docstrings, imports (handled by ruff+isort), error handling, formatting. Research conventions: reproducible seeds, logging, pathlib, no magic numbers, checkpoint saving | `/implement`, `/experiment`, `/debug`, `/integrate`, `/code-quality` |
| `{{ COMPLETION_PROTOCOL }}` | `blocks/completion-protocol.md` | Status reporting: DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT. Escalation format with reason, attempted, recommendation | All 21 skills |
| `{{ LEARNINGS_EPILOGUE }}` | `blocks/learnings-epilogue.md` | End-of-session reflection: did commands fail? wrong approach? project quirks? Appends to `~/.resskills/projects/{slug}/learnings.md` under the matching section (Techniques/Pitfalls/Insights/Conventions) | All 21 skills |
| `{{ ROUTING_RULES }}` | `blocks/routing-rules.md` | Natural language -> skill mapping: "run experiments" -> `/experiment`, "analyze results" -> `/analyze`, etc. 20 routing rules covering all skills | Root SKILL.md only |
| `{{ REVIEW_RUBRIC }}` | `blocks/review-rubric.md` | 5-dimension quality rubric (0-100): methodology, evidence, clarity, originality, writing. Decision mapping: >=80 accept, 65-79 minor revision, 50-64 major revision, <50 reject | `/review`, `/paper-review` |
| `{{ WRITING_QUALITY_CHECK }}` | `blocks/writing-quality-check.md` | De-AI polish: 5 categories of AI-typical patterns to detect and fix (overused terms, structural monotony, throat-clearing, em dash overuse, formulaic transitions) | `/paper-write` |
| `{{ VENUE_FORMATS }}` | `blocks/venue-formats.md` | LaTeX specs per venue: NeurIPS (9pp), ICML (8pp), ICLR (9pp, author-year), CVPR (8pp), ACL (8pp long/4pp short). General LaTeX best practices (booktabs, cleveref, vector figures) | `/paper-write`, `/paper-compile` |
| `{{ SKILL_NAME }}` | auto-generated | The skill's directory name (e.g., `experiment`, `review`). Injected automatically by `resskills-gen`, not from a block file | All 21 skills (in learnings epilogue) |

### Creating a new placeholder

1. Create `blocks/my-new-block.md` with the content
2. Use `{{ MY_NEW_BLOCK }}` in any `.tmpl` file (filename stem, uppercased, hyphens -> underscores)
3. Run `uv run resskills-gen`

The generator auto-discovers all `.md` files in `blocks/`. No code changes needed.

### Why committed, not generated at runtime?

Three reasons:

1. **Claude reads SKILL.md at skill load time.** There's no build step when a user invokes `/experiment`. The file must already exist and be correct.
2. **CI can validate freshness.** `uv run resskills-gen --dry-run` exits 1 if any generated file is stale.
3. **Git blame works.** You can see when a block was added and in which commit.

## Config system

Config is loaded in the preamble at skill startup. Search order (first found wins):

1. `resskills.yaml` in project root (project-local)
2. `~/.resskills/config.yaml` (global user config)

There is no pack default. If no config exists, skills infer from context or ask.
See `config.example.yaml` for available options.

### Config variables

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `primary_metric` | `val_loss` | What `/experiment` optimizes |
| `metric_direction` | `lower_is_better` | `lower_is_better` or `higher_is_better` |
| `time_budget_min` | `5` | Fixed wall-clock minutes per experiment run |
| `gpu` | `auto` | `auto`, `cuda`, `mps`, or `cpu` |
| `train_command` | `python train.py` | What `/experiment` executes |
| `eval_command` | `python eval.py` | Evaluation script |
| `train_file` | `train.py` | The ONLY file `/experiment` modifies |
| `prepare_file` | `prepare.py` | Read-only data prep (never modified) |
| `results_file` | `experiments/results.tsv` | Experiment log location |
| `paper_format` | `latex` | Output format for paper skills |
| `venue` | `NeurIPS` | Target venue (controls page limits, citation style) |
| `protect_dirs` | `[experiments/, data/, checkpoints/]` | Directories `/careful` protects from deletion |
| `human_checkpoint` | `[hypothesis, paper-write]` | Skills that pause for user approval |

### Preamble output

Every skill prints context at startup. Only lines with actual data appear:

```
# Fresh project (nothing set up yet):
BRANCH: main | PROJECT: my-new-idea

# Mid-project (user has configured + run experiments):
BRANCH: experiment/attention | PROJECT: my-research
CONFIG: resskills.yaml
[full config contents printed]
RESULTS: experiments/results.tsv (12 runs)
STATE: research-state.yaml
FINDINGS: findings.md (45 lines)
LEARNINGS: ~/.resskills/projects/my-research/learnings.md (28 lines)
```

The preamble provides **context**, not instructions. No hardcoded defaults.
Skills use judgment to decide what they need from the current project state:
- Config exists → use its values
- No config but context is obvious → infer and proceed
- Ambiguous → ask the user

## Learnings system

Learnings are **per-project**, not global. The `{slug}` is the git repo directory name:

```
~/.resskills/
├── config.yaml                              ← global user config (optional)
└── projects/
    ├── my-attention-paper/learnings.md       ← learnings for project A
    ├── my-diffusion-model/learnings.md       ← learnings for project B
    └── my-rl-agent/learnings.md              ← learnings for project C
```

When you start a session in `my-attention-paper/`, the preamble loads **only that project's learnings**. "AdamW lr=3e-4 works best on this architecture" is specific to that project and shouldn't leak to your diffusion model project.

Format is plain Markdown (not JSONL -- human-readable, editable, Claude reads it natively):

```markdown
# Learnings

## Techniques
- AdamW lr=3e-4 + cosine schedule works best on this architecture (experiment, 2026-04-02)
- Gradient accumulation over 4 steps equivalent to 4x batch size (experiment, 2026-04-03)

## Pitfalls
- NaN loss when batch_size > 64 with lr > 0.001 (debug, 2026-04-02)

## Insights
- Performance plateaus after step 200 regardless of lr (analyze, 2026-04-02)

## Conventions
- Data lives in /data/v2/, not /data/ (setup-project, 2026-04-01)
```

Four sections:
- `Techniques` -- what works ("cosine schedule beats linear for this architecture")
- `Pitfalls` -- what breaks ("NaN at batch_size > 64")
- `Insights` -- what we discovered ("performance plateaus after step 200 regardless of lr")
- `Conventions` -- project patterns ("data lives in /data/v2/, not /data/")

The 5-minute test: only log if knowing this would save 5+ minutes in a future session.

## Skill roles

| Role | Skills | Research equivalent |
|------|--------|-------------------|
| Principal Investigator | `/pi-review`, `/retro` | Sets direction, evaluates scope |
| Research Scientist | `/lit-review`, `/hypothesis` | Literature, experiment design |
| Research Engineer | `/deep-research`, `/integrate` | Due diligence, 3rd party code |
| ML Engineer | `/implement`, `/experiment`, `/debug` | Code, training loops, debugging |
| Analyst / Reviewer | `/analyze`, `/review`, `/paper-review`, `/second-opinion` | Statistics, methodology audit |
| Technical Writer | `/paper-write`, `/paper-compile` | Paper drafting, LaTeX |
| Code Quality | `/code-quality` | Google Python Style enforcement |
| System | `/careful`, `/checkpoint`, `/learn`, `/setup-project` | Safety, state, knowledge |

## Two-loop architecture

Inspired by Orchestra AI-Research-SKILLs:

```
INNER LOOP (tight, metric-driven):
  /experiment: modify -> train -> evaluate -> keep/discard -> repeat

OUTER LOOP (reflective, every 5-10 experiments):
  /analyze: statistical significance, plots
  /review: methodology audit
  Update findings.md with narrative synthesis
  Decide: DEEPEN | BROADEN | PIVOT | CONCLUDE
```

`findings.md` bridges the two loops. It's the active memory that prevents repeating failed approaches and compounds insights across sessions.

## What's intentionally not here

- **No browser automation.** If you need it, install [gstack](https://github.com/garrytan/gstack) alongside resskills. The two packs coexist -- gstack handles `/browse`, `/qa`, `/ship`; resskills handles `/experiment`, `/review`, `/paper-write`. No conflicts.
- **No MCP servers.** Cross-model review uses Agent subagents, not external services.
- **No telemetry.** Personal research tool, not a product.
- **No multi-user support.** One researcher, one machine.
- **No framework lock-in.** Pure Markdown skills, Jinja2 for templating, that's it.
