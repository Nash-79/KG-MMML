# Results Narrative (Weeks 1–10)

This section ties the objectives, decision gates, and evidence into one view.

## Master Gate Table

| Gate | Target | Actual | Status | Evidence |
|------|--------|--------|--------|----------|
| HP (hierarchy) | ≥0.25 | 0.2726 | PASS | srs_kge_combined.csv |
| AtP (units) | ≥0.95 | 0.9987 | PASS | srs_kge_combined.csv |
| AP (direction) | ≥0.99 | 1.0000 | PASS | srs_kge_combined.csv |
| SRS (overall) | ≥0.75 | 0.7571 | PASS | srs_kge_combined.csv |
| Latency p99 | <150ms | 0.037ms (Annoy) | PASS | latency_baseline_combined.csv |
| +3pp micro‑F1 | ≥+3.0pp | +1.36pp | FAIL | baseline_vs_joint_comprehensive_w9.csv |
| Stability (std) | <0.05 | 0.000 | PASS | srs_stability_w9.csv |

## What the results mean
- I preserved semantics (SRS > 0.75) while delivering sub‑millisecond retrieval.
- Auto‑taxonomy fixed the main bottleneck (HP), lifting overall SRS.
- Consistency penalty doesn’t help; simpler model (λ=0.0) performs better.
- Concept features help classification substantially, though the +3pp micro‑F1 gate was too strict given near‑perfect absolute accuracy.

## Decisions taken (M5 Complete)
- Adopt sklearn text+concept baseline as production default.
- Keep λ=0.0 (penalty OFF); enforce hierarchy post‑hoc if required.
- Use SRS (HP/AtP/AP) as ongoing quality monitor; expect zero variance.
- **+3pp gate discussion**: Gate missed due to ceiling effect (baseline at 98.32%). Macro-F1 improvement (+2.27pp) and SRS (0.7571) demonstrate KG value. Research contribution is the framework, not hitting arbitrary percentage threshold.
- **Joint objective conclusion**: Consistency penalty (λ>0) adds complexity without benefit. Simpler model wins.

## M5 Analysis (Week 9-10)

**What I tested**: Joint objective with consistency penalty on directional edges (λ ∈ {0.0, 0.1, 0.5}).

**Result**: λ=0.0 (no penalty) outperforms all constrained variants:
- λ=0.0: 99.68% micro-F1, 81.28% macro-F1 (stable)
- λ=0.1: 99.21% micro-F1, 80.15% macro-F1 (unstable training)
- λ=0.5: 98.87% micro-F1, 79.42% macro-F1 (very unstable)

**Why penalty doesn't help**:
1. Concept features already capture hierarchy through co-occurrence
2. Classification loss conflicts with consistency loss
3. SEC EDGAR data doesn't violate hierarchy (nothing to penalize)

**Production choice**: sklearn text+concept baseline (λ=0.0). Simple, fast, stable, better.

See [docs/M5_COMPLETE.md](M5_COMPLETE.md) for full analysis.

## Open items
- **M6 (W11-12)**: Consolidate metrics, tidy outputs, prepare for robustness
- **M7 (W13-14)**: Robustness tests (taxonomy off, noisy units)
- **M8 (W15-16)**: Scalability exploration (two-hop+vector, domain vs generic)
- Implement RTF to complete SRS (embedding‑based) - future work
- Expand manual taxonomy incrementally for coverage in edge cases
