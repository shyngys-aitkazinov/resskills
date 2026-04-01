# resskills

Virtual AI research team for Claude Code. 21 skills that turn a solo AI/CS researcher into a team of PI, Research Scientist, ML Engineer, Analyst, Reviewer, and Technical Writer.

## Quick Start

```bash
# Install
git clone <repo> ~/.claude/skills/resskills
cd ~/.claude/skills/resskills
uv sync
uv run python scripts/gen_skills.py

# Initialize a research project
cd ~/my-research-project
# Then in Claude Code:
/setup-project
```

## Skills Reference

### Direction & Strategy
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/pi-review` | Evaluates research direction | "Is this idea worth pursuing?" |
| `/retro` | Weekly retrospective | "What patterns emerged this week?" |

### Ideas & Hypotheses
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/lit-review` | Literature search + novelty check | "What's the state of the art?" |
| `/hypothesis` | Experiment design with controls | "Design an experiment to test X" |

### Due Diligence & Integration
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/deep-research` | Find existing tools, libs, repos | "What already exists for X?" |
| `/integrate` | Integration strategy for 3rd party code | "How should we use this repo?" |

### Code & Experiments
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/implement` | Write ML code (Google Python Style) | "Write the training loop" |
| `/experiment` | Autonomous experiment loop (~12/hour) | "Run experiments overnight" |
| `/debug` | Scientific-method debugging | "Why is loss NaN?" |

### Analysis & Review
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/analyze` | Statistical analysis + plots | "Are these results significant?" |
| `/review` | Adversarial methodology check | "Check for data leakage" |
| `/paper-review` | Simulate conference reviewer (scored 0-100) | "Would NeurIPS accept this?" |
| `/second-opinion` | Independent verification via subagent | "Get a fresh pair of eyes" |

### Paper Writing
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/paper-write` | Draft sections with verified citations | "Write the introduction" |
| `/paper-compile` | LaTeX -> PDF + pre-submission check | "Compile the paper" |

### Code Quality
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/code-quality` | ruff + mypy + Google style enforcement | "Check code quality" |

### System
| Command | What it does | When to use |
|---------|-------------|-------------|
| `/careful` | Safety hooks (protects experiment data) | "Be careful with my data" |
| `/checkpoint` | Save/resume research state | "Save progress" / "Where was I?" |
| `/learn` | Cross-session knowledge management | "What have we learned?" |
| `/setup-project` | Initialize research project structure | First time in a new project |

## Workflows

### The Experiment Loop (overnight)
```
/hypothesis --> /implement --> /experiment --> /checkpoint
# Wake up to ~100 experiments completed
```

### Full Research Cycle
```
/pi-review --> /lit-review --> /hypothesis --> /deep-research
--> /integrate --> /implement --> /experiment --> /checkpoint
--> /analyze --> /review --> /paper-write --> /paper-compile
```

### Quick Analysis
```
/analyze --> /review --> /second-opinion
```

## Configuration

Edit `config.yaml` in the skills root:

```yaml
primary_metric: val_loss          # What /experiment optimizes
metric_direction: lower_is_better
time_budget_min: 5                # Fixed time per experiment
train_command: "python train.py"
train_file: train.py
venue: NeurIPS                    # Paper formatting target
```

## Creating New Skills

```bash
mkdir my-skill/
# Create SKILL.md.tmpl with {{ PREAMBLE }} + your content + {{ COMPLETION_PROTOCOL }}
uv run python scripts/gen_skills.py
# Done!
```

See `blocks/` for available shared blocks:

| Block | What it injects |
|-------|----------------|
| `{{ PREAMBLE }}` | Branch, experiment count, best metric, learnings |
| `{{ VOICE }}` | Tone rules: precise, evidence-based |
| `{{ PYTHON_STANDARDS }}` | Google Python Style + research conventions |
| `{{ COMPLETION_PROTOCOL }}` | DONE / BLOCKED status reporting |
| `{{ LEARNINGS_EPILOGUE }}` | End-of-session learning log |
| `{{ ROUTING_RULES }}` | Natural language -> skill routing |
| `{{ REVIEW_RUBRIC }}` | 5-dimension quality rubric (0-100) |
| `{{ WRITING_QUALITY_CHECK }}` | AI writing anti-patterns |
| `{{ VENUE_FORMATS }}` | NeurIPS/ICML/ICLR/CVPR LaTeX specs |

## Project Structure (created by /setup-project)

```
my-research/
├── experiments/
│   ├── results.tsv              # Experiment log
│   └── checkpoints/             # Research state snapshots
├── data/                        # Datasets (protected by /careful)
├── checkpoints/                 # Model checkpoints (protected)
├── paper/                       # LaTeX source
├── figures/                     # Generated plots
├── train.py                     # The file /experiment modifies
├── eval.py                      # Evaluation (read-only during /experiment)
├── research-state.yaml          # Machine-readable research state
└── findings.md                  # Narrative synthesis of what we know
```

## Architecture

resskills uses a template system inspired by [gstack](https://github.com/garrytan/gstack):

- Each skill has a `SKILL.md.tmpl` (source of truth) and a generated `SKILL.md`
- Shared blocks in `blocks/` are injected via Jinja2 (`{{ BLOCK_NAME }}`)
- `uv run python scripts/gen_skills.py` regenerates all skills from templates
- Change a block once, regenerate, and all 21 skills update

### Template System

```
blocks/*.md           (shared prose + instructions)
       |
       v
SKILL.md.tmpl         (human-written per-skill content + {{ placeholders }})
       |
       v  [uv run python scripts/gen_skills.py]
SKILL.md              (generated, committed, what Claude Code reads)
```

## Inspired By

- [gstack](https://github.com/garrytan/gstack) -- skill architecture, template system, safety hooks
- [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) -- experiment loop pattern
- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) -- research pipeline, cross-model review
- [Orchestra AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) -- two-loop architecture
- [Academic Research Skills](https://github.com/Imbad0202/academic-research-skills) -- quality rubrics, integrity verification
