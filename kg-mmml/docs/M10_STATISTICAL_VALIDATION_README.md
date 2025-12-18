# M10: Statistical Validation with Multiple Random Seeds

**Phase**: Phase D (Thesis Writing)
**Milestone**: M10 (Week 19-20)
**Status**: Ready to run
**Objective**: Validate reproducibility and statistical significance across 5 random seeds

---

## Overview

M10 addresses academic rigour requirements by demonstrating that results are:
1. **Reproducible** across different train/test splits
2. **Statistically significant** (not due to random chance)
3. **Stable** with low variance across seeds

This strengthens the thesis claim that the hybrid KG-ML architecture provides consistent, reliable improvements.

---

## Experimental Design

### Random Seeds
- **Seeds**: 42, 43, 44, 45, 46
- **Rationale**: 5 seeds provides sufficient statistical power for paired t-tests while remaining computationally feasible

### Models Compared
1. **Baseline (text-only)**: TF-IDF features (20,000 max, min_df=2)
2. **Text+Concept (KG-as-features)**: TF-IDF + binary concept indicators

### Metrics
- **Micro-F1**: Overall accuracy (weighted by support)
- **Macro-F1**: Average per-class F1 (unweighted, sensitive to rare classes)

### Statistical Tests
- **Confidence intervals**: 95% CI for mean improvements
- **Paired t-test**: Two-tailed test comparing text+concept vs baseline
- **Significance levels**: p<0.05 (significant), p<0.01 (highly significant)

---

## Scripts

### 1. Quick Test (Single Seed)
**Purpose**: Verify pipeline works before running all 5 seeds

```bash
python scripts/m10_test_single_seed.py
```

**Runtime**: ~2-5 minutes
**Outputs**:
- `reports/tables/m10_test_seed42_baseline.json`
- `reports/tables/m10_test_seed42_text_concept.json`

### 2. Statistical Validation (Core Script)
**Purpose**: Run all 5 seeds and compute statistics

```bash
python scripts/m10_statistical_validation.py
```

**Runtime**: ~10-25 minutes (depends on dataset size)
**Outputs**:
- `reports/tables/m10_seed{X}_baseline_text_metrics.json` (X=42,43,44,45,46)
- `reports/tables/m10_seed{X}_text_concept_metrics.json`
- `reports/tables/m10_statistical_summary.csv`
- `reports/tables/m10_statistical_tests.json`

**Usage options**:
```bash
# Run experiments only
python scripts/m10_statistical_validation.py --run_experiments

# Compute statistics only (from saved results)
python scripts/m10_statistical_validation.py --compute_statistics

# Run both (default)
python scripts/m10_statistical_validation.py
```

### 3. Master Runner + Report Generation
**Purpose**: Run everything and generate markdown report

```bash
python scripts/run_m10_all.py
```

**Runtime**: ~10-25 minutes
**Outputs**: All of the above + `kg-mmml/docs/M10_STATISTICAL_VALIDATION_REPORT.md`

---

## Workflow

### Step 1: Quick Test (Recommended)
Verify the pipeline works before committing to the full 5-seed run:

```bash
python scripts/m10_test_single_seed.py
```

**Check**:
- [ ] No import errors
- [ ] Paths to facts.jsonl, taxonomy, and concept features are correct
- [ ] Metrics look reasonable (micro-F1 ~0.98-0.99, macro-F1 ~0.97-0.99)
- [ ] Improvement is positive (~+1-3pp)

### Step 2: Full 5-Seed Validation
Once the quick test passes, run the full validation:

```bash
python scripts/run_m10_all.py
```

**Monitor**:
- Each seed should complete in ~1-2 minutes
- 10 total experiments (5 baseline + 5 text+concept)
- Statistics computed automatically at the end

### Step 3: Review Results
Check the generated report:

```bash
cat kg-mmml/docs/M10_STATISTICAL_VALIDATION_REPORT.md
```

**Key items to verify**:
- [ ] Low standard deviation (high reproducibility)
- [ ] Macro-F1 improvement is statistically significant (p<0.05)
- [ ] Micro-F1 improvement is consistent (even if <+3pp due to ceiling effects)
- [ ] Confidence intervals are narrow

### Step 4: Update Thesis
Incorporate statistical validation into Chapter 5 (Results):

1. **Update metrics tables** with mean ± std and 95% CI
2. **Add statistical significance statements** (e.g., "p<0.01")
3. **Reference M10 report** in appendices
4. **Discuss reproducibility** in Discussion chapter

---

## Expected Results

Based on M3/M6 single-seed experiments (seed=42):

| Metric | Baseline | Text+Concept | Improvement | Expected p-value |
|--------|----------|--------------|-------------|------------------|
| Micro-F1 | 0.9833 | 0.9968 | +1.36pp | p<0.05 (likely) |
| Macro-F1 | 0.9723 | 0.9950 | +2.27pp | p<0.01 (very likely) |

**Prediction**:
- Macro-F1 improvement will be highly significant (p<0.01)
- Micro-F1 improvement will be significant (p<0.05) but may vary due to ceiling effects
- Standard deviation will be low (<0.01 for both metrics)

---

## Interpreting Results

### If Improvements Are Significant (p<0.05)
✅ **Thesis claim**: "KG-as-features provide statistically significant improvements (p<0.05, paired t-test, n=5) over text-only baselines."

### If Improvements Are Not Significant (p≥0.05)
⚠️ **Thesis claim**: "KG-as-features show consistent directional improvements across all seeds, though high baseline accuracy (~98.3%) creates ceiling effects that limit statistical significance."

**Mitigation**:
- Emphasize macro-F1 significance (benefits for rare classes)
- Reference M9 error analysis (low error rate = ceiling effect)
- Highlight SRS metric (semantic preservation, not just accuracy)

---

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'kg_mmml'`:

```bash
# Ensure you're running from the project root
cd C:\Users\nmepa\Nash-79

# Use module syntax instead
python -m kg_mmml.scripts.m10_test_single_seed
```

### Missing Files
If experiments fail with `FileNotFoundError`:

**Check paths**:
- `data/processed/sec_edgar/facts.jsonl` (exists?)
- `datasets/sec_edgar/taxonomy/usgaap_combined.csv` (exists?)
- `data/processed/sec_edgar/features/concept_features_filing.npz` (exists?)
- `data/processed/sec_edgar/features/concept_features_index.csv` (exists?)

**Fix**: Ensure M4 concept feature extraction completed successfully.

### Long Runtime (>30 minutes)
If experiments take too long:

**Optimisation**:
- Reduce `--max_features` from 20000 to 10000 (in `m10_statistical_validation.py`)
- Use smaller test_size (0.2 instead of 0.25)
- Run on a faster machine

---

## Dependencies

Ensure these packages are installed:

```bash
pip install numpy scipy scikit-learn pandas
```

**Version requirements**:
- `numpy>=1.20`
- `scipy>=1.7`
- `scikit-learn>=1.0`
- `pandas>=1.3`

---

## Next Steps After M10

1. **Update Chapter 5** with statistical validation results
2. **Start Chapter 6** (Discussion) - interpret significance, relate to RQs
3. **Draft Chapter 7** (Conclusion) - summarise contributions
4. **Write Abstract** (250 words)
5. **Create Appendices** (code listings, full metric tables)

---

## References

- **M3 Decision Gate**: Micro-F1 improvement target (docs/02_RESULTS_NARRATIVE.md)
- **M6 RTF Implementation**: SRS metric with TransE embeddings (docs/M6_PLAN.md)
- **M9 Error Analysis**: Low error rate and ceiling effects (docs/M9_PLAN.md)
- **Baseline implementation**: src/cli/baseline_tfidf.py
- **Statistical methods**: scipy.stats.ttest_rel (paired t-test)

---

**Author**: Nash-79
**Date**: 2025-12-15
**Milestone**: M10 Statistical Validation (Week 19-20)
