# Experiment Plan: [TITLE]

## Research Question
[What specific question does this experiment answer?]

## Hypothesis
[Testable prediction with expected direction of effect]

## Independent Variables
- [What you change between conditions]

## Dependent Variables (Metrics)
- **Primary:** [single metric to optimize, e.g., val_loss]
- **Secondary:** [other metrics to track, e.g., training_time, memory_gb]

## Controls
- **Baseline:** [what to compare against]
- **Ablations:** [what to remove to test each component's contribution]

## Protocol
1. [Step-by-step procedure]
2. [Be specific about hyperparameters, data splits, seeds]

## Time Budget
- Per experiment: [X min]
- Estimated runs: [N runs]
- Total wall-clock: [X * N min]

## Success Criteria
- Minimum improvement over baseline: [threshold, e.g., > 0.5% val_loss reduction]
- Statistical test: [paired t-test / bootstrap / permutation test]
- Required significance level: [p < 0.05]

## Risks & Mitigations
- [What could go wrong and how to handle it]
- [E.g., OOM: reduce batch size; NaN: gradient clipping]
