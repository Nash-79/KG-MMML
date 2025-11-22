# Week 9 Execution Plan: Milestone M5

**Phase B, Milestone M5: Minimal Joint Objective + Trade-offs**  
**Timeline:** Week 9 (Oct 25 – Oct 31, 2025)  
**Status:** In Progress

---

## Overview

This week focuses on completing Phase B's Milestone M5, which validates the minimal joint objective approach and documents critical trade-offs between text-only baselines, joint models, and consistency penalty configurations. We will also establish SRS metric stability through multi-seed validation.

### Success Criteria (Decision Gates)
1. **Baseline F1 Gate**: Text+concept joint model achieves ≥+3pp micro-F1 improvement over text-only baseline
2. **SRS Stability Gate**: SRS metric shows std deviation < 0.05 across 5 random seeds
3. **Documentation Gate**: All trade-offs documented with reproducible configs and acceptance CSVs

---

## Week 9 Primary Goals

### **Goal 1: Baseline F1 Validation** (Carryover from M4)

**Objective:** Validate that the joint model (text+concept features) provides measurable improvement over text-only baseline when using identical train/test splits.

#### Tasks
1. **Rerun Text-Only Baseline**
   - Command: `python src/cli/baseline_tfidf.py --seed 42 --split matched`
   - Use same train/test split as joint model (seed=42)
   - Generate predictions on test set
   - Compute macro-F1 and micro-F1 metrics
   - Output: `reports/tables/baseline_text_seed42_metrics.json`

2. **Compare Baseline vs Joint Model**
   - Extract joint model metrics (λ=0.0, macro-F1=81.28%) from `outputs/joint_no_penalty/metrics.json`
   - Create comparison CSV with columns: `[model, macro_f1, micro_f1, improvement_micro_f1]`
   - Validate decision gate: micro-F1 improvement ≥ 3pp
   - Output: `reports/tables/baseline_vs_joint_comparison.csv`

3. **Decision Gate Checkpoint**
   - If gate passes (): Proceed to Goal 2
   - If gate fails (): Debug joint model feature engineering or revisit concept extraction

#### Acceptance Criteria
- CSV file with text-only vs text+concept comparison exists
- Decision gate status confirmed (pass/fail) in CSV or separate status file
- Reproducible command documented in `WEEK9_PLAN.md`

#### Timeline
- **Day 1 (Oct 25):** Rerun baseline with matched splits
- **Day 2 (Oct 26):** Generate comparison CSV and validate gate

---

### **Goal 2: Joint Model Refinement**

**Objective:** Document the trade-off between macro-F1 performance and consistency penalty strength (λ), and establish λ=0.0 as the default configuration based on empirical evidence.

#### Tasks
1. **Document Consistency Penalty Trade-off**
   - Analyze existing results:
     - λ=0.0 (penalty OFF): macro-F1=81.28%, micro-F1=TBD
     - λ>0 (penalty ON): macro-F1=79.95%, micro-F1=TBD
   - Document observations:
     - Stronger penalty (λ>0) reduces constraint violations but degrades macro-F1 by ~1.3pp
     - Hypothesis: Penalty regularizes too aggressively for this taxonomy structure
   - Add technical analysis section to `reports/EXPERIMENT_RESULTS_SUMMARY.md`
   - Output: Updated documentation with trade-off analysis

2. **Update Default Configuration**
   - Modify `configs/experiment_joint.yaml`:
     ```yaml
     consistency_penalty: 0.0  # Default: penalty OFF based on W7-8 ablation (macro-F1=81.28% vs 79.95%)
     # Note: Set to 0.01 or 0.05 for constraint-sensitive applications
     ```
   - Add inline comments explaining rationale
   - Output: Updated `configs/experiment_joint.yaml`

3. **Optional: λ Sensitivity Analysis**
   - Test intermediate values: λ ∈ {0.01, 0.05}
   - Commands:
     ```bash
     python src/cli/train_joint.py --config configs/experiment_joint.yaml --penalty 0.01 --output outputs/joint_lambda_001
     python src/cli/train_joint.py --config configs/experiment_joint.yaml --penalty 0.05 --output outputs/joint_lambda_005
     ```
   - Compare macro-F1, micro-F1, and constraint violation rates
   - Generate sensitivity plot: `reports/figures/lambda_sensitivity_w9.png`
   - Output: Extended ablation results in `reports/tables/joint_lambda_ablation_extended.csv`

#### Acceptance Criteria
- Trade-off analysis added to `EXPERIMENT_RESULTS_SUMMARY.md`
- `configs/experiment_joint.yaml` updated with λ=0.0 default and rationale comments
- (Optional) Sensitivity analysis completed with λ ∈ {0.01, 0.05} results

#### Timeline
- **Day 3 (Oct 27):** Document penalty trade-off analysis
- **Day 4 (Oct 28):** Update configs and run optional sensitivity tests
- **Day 5 (Oct 29):** Generate sensitivity plot if optional task completed

---

### **Goal 3: SRS Stability Check**

**Objective:** Validate that the SRS metric (Semantic Relationship Score) is stable across different random seeds, ensuring reproducibility and confidence in taxonomy quality measurements.

#### Tasks
1. **Implement Multi-Seed SRS Script**
   - Create `scripts/compute_srs_stability.py`
   - Reuse logic from `src/cli/compute_srs.py`
   - Loop over seeds: [42, 43, 44, 45, 46]
   - For each seed:
     - Load `datasets/sec_edgar/taxonomy/usgaap_combined.csv`
     - Compute HP (Hierarchy Precision), AtP (Ancestor-to-Precision), AP (Average Precision), SRS
     - Store results with seed identifier
   - Compute aggregate statistics: mean ± std for each metric
   - Output: `reports/tables/srs_stability_w9.csv`

2. **Execute SRS Stability Check**
   - Command: `python scripts/compute_srs_stability.py --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv --seeds 42 43 44 45 46 --output reports/tables/srs_stability_w9.csv`
   - Expected runtime: ~5-10 minutes (5 iterations)
   - Verify results:
     - Mean SRS ≈ 0.757 (from W7-8 baseline)
     - Std SRS < 0.05 (stability threshold)
   - Decision gate: If std > 0.05, investigate seed-dependent variance sources

3. **Generate Confidence Interval Report**
   - Format CSV with columns: `[metric, mean, std, ci_lower, ci_upper, seeds_tested]`
   - Example row: `SRS, 0.757, 0.012, 0.745, 0.769, [42,43,44,45,46]`
   - Add summary row: `DECISION_GATE, PASS/FAIL, std_threshold=0.05`
   - Output: Final `reports/tables/srs_stability_w9.csv`

#### Acceptance Criteria
- `scripts/compute_srs_stability.py` created and executable
- `reports/tables/srs_stability_w9.csv` contains mean ± std for HP, AtP, AP, SRS
- Confidence intervals (95% CI) reported for each metric
- Decision gate status (std < 0.05) confirmed

#### Timeline
- **Day 6 (Oct 30):** Implement multi-seed SRS script
- **Day 7 (Oct 31):** Run stability check and generate final CSV report

---

## Deliverables Summary

### Files to Create/Update
| File | Type | Description |
|------|------|-------------|
| `reports/tables/baseline_text_seed42_metrics.json` | NEW | Text-only baseline metrics with seed=42 |
| `reports/tables/baseline_vs_joint_comparison.csv` | NEW | Baseline vs joint model comparison with decision gate |
| `reports/EXPERIMENT_RESULTS_SUMMARY.md` | UPDATE | Add λ trade-off analysis section |
| `configs/experiment_joint.yaml` | UPDATE | Set λ=0.0 as default with rationale comments |
| `outputs/joint_lambda_001/metrics.json` | NEW (Optional) | λ=0.01 sensitivity test results |
| `outputs/joint_lambda_005/metrics.json` | NEW (Optional) | λ=0.05 sensitivity test results |
| `reports/tables/joint_lambda_ablation_extended.csv` | NEW (Optional) | Extended ablation with λ sensitivity |
| `reports/figures/lambda_sensitivity_w9.png` | NEW (Optional) | Sensitivity plot for λ parameter |
| `scripts/compute_srs_stability.py` | NEW | Multi-seed SRS computation script |
| `reports/tables/srs_stability_w9.csv` | NEW | SRS stability report with confidence intervals |
| `scripts/visualization/plot_baseline_vs_joint.py` | NEW | Visualization for baseline vs joint comparison |
| `reports/figures/baseline_vs_joint_w9.png` | NEW | Macro-F1 and micro-F1 comparison chart |
| `tests/test_baseline_validation.py` | NEW | Tests for baseline model correctness |
| `WEEK9_COMPLETION.md` | NEW | Week 9 summary report with all results |

### Metrics to Track
- **Baseline Metrics**: macro-F1, micro-F1 for text-only model (seed=42)
- **Joint Model Metrics**: macro-F1=81.28%, micro-F1 (to be extracted)
- **Improvement**: Δ micro-F1 (target: ≥3pp)
- **SRS Stability**: mean ± std for HP, AtP, AP, SRS across 5 seeds
- **λ Sensitivity**: macro-F1, micro-F1, constraint violations for λ ∈ {0.0, 0.01, 0.05}

---

## Risk Mitigation

### Risk 1: Baseline F1 Gate Fails (micro-F1 improvement < 3pp)
- **Mitigation:** Debug concept feature extraction in `make_concept_features.py`
- **Fallback:** Revisit taxonomy structure or increase concept feature weight in joint model

### Risk 2: SRS Stability Gate Fails (std > 0.05)
- **Mitigation:** Investigate seed-dependent variance (e.g., embedding initialization, sampling)
- **Fallback:** Increase seed count to 10 or use fixed embedding seeds

### Risk 3: Optional λ Sensitivity Tests Take Too Long
- **Mitigation:** Run only λ=0.01 if time-constrained
- **Fallback:** Document as "future work" and proceed with λ=0.0 default

---

## Next Steps (Week 10 Preview)

After completing Week 9 goals:
1. **Week 10 Goal 1:** Multi-modal latency optimization (target: <100ms p99)
2. **Week 10 Goal 2:** Full pipeline integration test (taxonomy → features → joint model → retrieval)
3. **Week 10 Goal 3:** Production readiness checklist (logging, error handling, CI/CD)

---

## Reproducibility Commands

### Quick Start (All Goals)
```bash
# Goal 1: Baseline validation
python src/cli/baseline_tfidf.py --seed 42 --split matched --output reports/tables/baseline_text_seed42_metrics.json
python scripts/compare_baseline_vs_joint.py --baseline reports/tables/baseline_text_seed42_metrics.json --joint outputs/joint_no_penalty/metrics.json --output reports/tables/baseline_vs_joint_comparison.csv

# Goal 2: λ sensitivity (optional)
python src/cli/train_joint.py --config configs/experiment_joint.yaml --penalty 0.01 --output outputs/joint_lambda_001
python src/cli/train_joint.py --config configs/experiment_joint.yaml --penalty 0.05 --output outputs/joint_lambda_005

# Goal 3: SRS stability
python scripts/compute_srs_stability.py --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv --seeds 42 43 44 45 46 --output reports/tables/srs_stability_w9.csv
```

### Verification Commands
```bash
# Check baseline metrics exist
test -f reports/tables/baseline_text_seed42_metrics.json && echo "Baseline metrics generated"

# Check decision gate status
grep "PASS\|FAIL" reports/tables/baseline_vs_joint_comparison.csv

# Check SRS stability
grep "DECISION_GATE" reports/tables/srs_stability_w9.csv
```

---

**Document Version:** 1.0  
**Last Updated:** October 25, 2025  
**Owner:** Nash-79 / KG-MMML Project  
**Status:** Ready for execution
