# Evaluation Checklist (M5 Results)

**Project**: KG-MMML
**Phase**: B Complete (W5-10)
**Date**: October 27, 2025

## Semantic Retention (SRS)
- [x] AtP ≥ 0.95: **0.9987** PASS
- [x] HP ≥ 0.25: **0.2726** PASS (auto-taxonomy coverage)
- [x] AP ≥ 0.99: **1.0000** PASS (directional integrity)
- [x] SRS ≥ 0.75: **0.7571** PASS (weighted: 0.25×HP + 0.20×AtP + 0.20×AP + 0.35×RTF*)

*RTF not yet implemented; using placeholder weight redistribution

## Task Performance (sklearn baseline)
- [x] Baseline (text-only) micro-F1: **98.32%**
- [x] KG (text+concept) micro-F1: **99.68%**
- [ ] Delta ≥ +3pp: **+1.36pp** FAIL

**Note**: Ceiling effect at 98.32% baseline. Macro-F1 improvement: +2.27pp ## Latency (N=3,218, Annoy 20 trees)
- [x] p50 < 50ms: **0.027ms** PASS
- [x] p95 < 150ms: **0.038ms** PASS
- [x] p99 < 150ms: **0.048ms** PASS
- [x] p99/p95 ratio < 2.0: **1.26** PASS (0.048/0.038)

## Reproducibility
- [x] Seeds fixed: **42** (primary), [13, 17, 23, 29, 31] planned for M10
- [x] Configs pinned: **Yes** (configs/experiment_*.yaml)
- [x] Data snapshot: **data/kg/sec_edgar_2025-10-11** (pinned)
- [x] Deterministic metrics: **Yes** (SRS σ=0.000)

## Joint Objective Analysis (M5)
- [x] Consistency penalty tested: λ ∈ {0.0, 0.1, 0.5}
- [x] Result: λ=0.0 outperforms constrained variants
- [x] Production choice: **λ=0.0** (simple model wins)

## Gate Summary (2/3 Pass)
| Gate | Target | Actual | Status |
|------|--------|--------|--------|
| SRS | ≥0.75 | 0.7571 | PASS |
| Latency p99 | <150ms | 0.048ms | PASS |
| +3pp micro-F1 | ≥3.0pp | +1.36pp | FAIL* |

*Ceiling effect documented; macro-F1 +2.27pp demonstrates KG value

## Production Configuration
- **Model**: sklearn LogisticRegression
- **Features**: TF-IDF (50k max features) + one-hot concepts (4,502 dims)
- **Training**: `random_state=42`, `test_size=0.25`, stratified splits
- **Performance**: 99.68% micro-F1, 81.28% macro-F1
- **Latency**: 0.048ms p99 at N=3,218

## Next Phase (C: W11-18)
- [ ] M6: Consolidate metrics
- [ ] M7: Robustness tests (taxonomy off, unit noise)
- [ ] M8: Scalability exploration
- [ ] M9: Error analysis + Results draft