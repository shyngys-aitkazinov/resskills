## Skill Routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

**Routing rules -- when you see these patterns, INVOKE the skill:**
- "Is this idea worth pursuing", research direction, scope -> invoke `/pi-review`
- "What's the state of the art", related work, literature, papers on X -> invoke `/lit-review`
- "Design an experiment", hypothesis, "how to test X" -> invoke `/hypothesis`
- "What tools exist for", "what libraries", "find repos for" -> invoke `/deep-research`
- "How to integrate", "use this repo", "add this library" -> invoke `/integrate`
- "Write the training code", implement, "code the model" -> invoke `/implement`
- "Run experiments", "start the loop", "overnight run" -> invoke `/experiment`
- "Why is loss NaN", debug, "fix this error", broken -> invoke `/debug`
- "Analyze results", "is this significant", "plot the" -> invoke `/analyze`
- "Check methodology", "data leakage", "review my approach" -> invoke `/review`
- "Would NeurIPS accept", "simulate reviewer", "rate this paper" -> invoke `/paper-review`
- "Get a second opinion", "independent check" -> invoke `/second-opinion`
- "Write the introduction", "draft the method section" -> invoke `/paper-write`
- "Compile the paper", "build PDF", "check LaTeX" -> invoke `/paper-compile`
- "Check code quality", "run ruff", "type check" -> invoke `/code-quality`
- "Be careful", "safety mode", "protect my data" -> invoke `/careful`
- "Save progress", "where was I", checkpoint -> invoke `/checkpoint`
- "What have we learned", learnings, "past patterns" -> invoke `/learn`
- "Initialize project", "set up experiment structure" -> invoke `/setup-project`
- "Weekly retro", "what worked this week" -> invoke `/retro`

**Do NOT answer directly when a matching skill exists.** Invoke the skill first.
