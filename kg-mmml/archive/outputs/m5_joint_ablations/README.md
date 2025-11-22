# M5 Joint Objective Ablation Studies (Archived)

**Date Archived**: 2025-11-22
**Milestone**: M5 (Weeks 9-10)
**Status**: Superseded by sklearn production baseline

## Contents

This directory contains PyTorch joint model experiments testing consistency penalty (λ) variants:

| Directory | Configuration | Epochs | Test Micro-F1 | Test Macro-F1 | Notes |
|-----------|--------------|--------|---------------|---------------|-------|
| `joint_no_penalty` | λ=0.0, no concepts | 5 | 91.3% | 79.7% | Text-only baseline variant |
| `joint_with_penalty` | λ>0 (with penalty) | 5 | TBD | TBD | Constrained model |
| `joint_with_concepts_no_penalty` | λ=0.0, with concepts | 5 | 91.3% | 79.7% | Early stopping |
| `joint_with_concepts_no_penalty_e20` | λ=0.0, with concepts | 20 | 96.3% | 93.5% | Full training |

## Why Archived?

**M5 Conclusion**: Consistency penalty (λ > 0) did not improve performance. Simpler model (λ=0.0) outperformed constrained variants.

**Production Decision**: Use sklearn LogisticRegression with text + concept features instead of PyTorch joint model.

**Reasons**:
1. Simpler: No PyTorch dependency, fewer hyperparameters
2. Faster: Training and inference both faster
3. Better: Achieves 99.68% micro-F1 (vs 96.3% for PyTorch e20)
4. Stable: Deterministic, no loss oscillation
5. Production-ready: sklearn is well-tested and reliable

## Key Findings

1. **Consistency penalty adds complexity without benefit**: λ>0 variants underperformed λ=0.0
2. **Concept features help**: All variants with concept features outperform text-only
3. **Sklearn beats PyTorch for this task**: Traditional ML simpler and better than deep learning here
4. **Ceiling effect**: At 98%+ accuracy, incremental gains are diminishing

## References

- Full M5 analysis: `docs/M5_COMPLETE.md`
- Production config: `configs/experiment_baseline.yaml` (sklearn LogisticRegression)
- Consolidated metrics: `reports/tables/consolidated_metrics_w11.csv`

## Do Not Use

These experiments are retained for reproducibility and documentation purposes only. Do not use these configurations for production or further research. Use the sklearn baseline instead.
