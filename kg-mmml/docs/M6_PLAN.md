# M6 Plan: Consolidation and Calibration (Week 11-12)

**Deliverable**: Consolidated SRS + task + p50/p95/p99 metrics; tidy outputs; calibration check.

## Tasks

### 1. Consolidate Metrics (Priority: HIGH)

Create single comprehensive report combining all Phase B results.

**File to create**: `reports/tables/consolidated_metrics_w11.csv`

**Content**:
```
Category,Metric,Value,Target,Status,Notes
SRS,HP,0.2726,≥0.25,PASS,Auto-taxonomy lifted from ~0%
SRS,AtP,0.9987,≥0.95,PASS,Nearly all concepts have units
SRS,AP,1.0000,≥0.99,PASS,No reverse edges
SRS,SRS_overall,0.7571,≥0.75,PASS,Weighted composite
Task,Baseline_microF1,98.32%,-,-,Text-only TF-IDF
Task,Joint_microF1,99.68%,-,-,Text + concept features
Task,Improvement_microF1,+1.36pp,≥3.0pp,FAIL,Ceiling effect
Task,Improvement_macroF1,+2.27pp,-,-,Helps rare classes
Latency_N1000,p50,0.022ms,-,PASS,Annoy 20 trees
Latency_N1000,p95,0.029ms,-,PASS,-
Latency_N1000,p99,0.038ms,<150ms,PASS,-
Latency_N3218,p50,0.027ms,-,PASS,-
Latency_N3218,p95,0.038ms,-,PASS,-
Latency_N3218,p99,0.048ms,<150ms,PASS,-
```

**Script** (optional):
```python
# scripts/consolidate_metrics.py
import pandas as pd
import json

# Read individual metric files
srs = pd.read_csv('reports/tables/srs_kge_combined.csv')
latency = pd.read_csv('reports/tables/latency_baseline_combined.csv')
baseline = json.load(open('reports/tables/baseline_text_seed42_metrics.json'))
joint = json.load(open('outputs/joint_with_concepts_no_penalty_e20/metrics.json'))

# Combine into single table
# ... (implementation)
```

### 2. Tidy Outputs Directory (Priority: MEDIUM)

**Current state**: outputs/ has multiple experimental runs from W5-10

**Goal**: Keep only final production configs; archive the rest.

**Actions**:
```bash
# Create archive directories
mkdir -p archive/week5-6_early_experiments
mkdir -p archive/week7-8_taxonomy_iterations
mkdir -p archive/week9-10_consistency_tests

# Move intermediate experiments to archive
mv outputs/joint_with_concepts_lambda0.1/ archive/week9-10_consistency_tests/
mv outputs/joint_with_concepts_lambda0.5/ archive/week9-10_consistency_tests/
# ... etc

# Keep only:
# - baseline_text_seed42_metrics.json (final baseline)
# - outputs/joint_with_concepts_no_penalty_e20/ (final joint model)
```

**Documentation**: Update `outputs/README.md` with directory structure and what each contains.

### 3. Calibration Check (Priority: LOW)

**Question**: Are model confidence scores well-calibrated?

**Approach**:
- If using sklearn LogisticRegression: Already calibrated (probabilities are trustworthy)
- If probabilities seem off: Run calibration plot (predicted probability vs actual frequency)

**Implementation**:
```python
# scripts/check_calibration.py
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

# Get predicted probabilities and true labels
y_prob = model.predict_proba(X_test)
y_true = y_test

# Plot calibration curve
prob_true, prob_pred = calibration_curve(y_true, y_prob[:, 1], n_bins=10)
plt.plot(prob_pred, prob_true, marker='o')
plt.plot([0, 1], [0, 1], linestyle='--')  # Perfect calibration line
plt.xlabel('Predicted probability')
plt.ylabel('Actual frequency')
plt.title('Calibration Curve')
plt.savefig('reports/figures/calibration_curve.png')
```

**Decision**: Only do this if needed for thesis. sklearn LogReg is typically well-calibrated.

### 4. Write Week 11-12 Summary (Priority: HIGH)

**File to create**: `docs/WEEK11-12_SUMMARY.md`

**Content outline**:
```markdown
# Week 11-12 Summary: Consolidation

## Milestone M6 Complete

All Phase B metrics consolidated. System passes 2/3 decision gates.

## Consolidated Results

[Table from consolidated_metrics_w11.csv]

## Phase B Achievements (Week 5-10)

- M3: Baseline + KG-as-features implemented
- M4: Auto-taxonomy (HP: 0% → 27.26%), latency harness (p99: 0.037ms)
- M5: Joint objective analysis (λ=0.0 wins; +3pp gate ceiling effect documented)

## Production System

**Deployed configuration**: sklearn text+concept baseline
- 99.68% micro-F1 (near ceiling)
- 81.28% macro-F1 (+2.27pp over text-only)
- 0.7571 SRS (semantic preservation achieved)
- 0.037ms p99 latency (sub-millisecond queries)

## Decisions for Phase C

- Use simple baseline for robustness tests (M7)
- Focus M8 scalability on graph-filtered retrieval
- M9 error analysis: investigate the 0.32% misclassifications

## Next Milestone

**M7 (W13-14)**: Robustness testing
- Taxonomy off test
- Unit noise injection (5-10%)
- Verify performance drop ≤10%
```

### 5. Update CLAUDE.md Status (Priority: LOW)

Update the "Current Status" section to reflect M5 completion and M6 start.

```markdown
## Current Status (Week 11-12)

Working on Milestone M6 (consolidation and calibration).

**M5 Complete**: Joint objective analysis showed λ=0.0 outperforms constrained variants.

**Decision gates:**
- SRS = 0.7571 - PASS - Latency p99 = 0.037ms - PASS - +3pp micro-F1 = +1.36pp - FAIL (ceiling effect documented) **Next steps**: Consolidate metrics, prepare for robustness tests (M7).
```

## Timeline

- **This week (W11)**: Consolidate metrics, tidy outputs
- **Next week (W12)**: Write summary, prepare for M7
- **W13-14 (M7)**: Robustness tests

## Deliverables Checklist

- [ ] `reports/tables/consolidated_metrics_w11.csv`
- [ ] `outputs/README.md` (document structure)
- [ ] Archive intermediate experiments
- [ ] `docs/WEEK11-12_SUMMARY.md`
- [ ] Optional: Calibration plot
- [ ] Update CLAUDE.md status

## Notes

M6 is mostly about organisation and documentation. No new experiments required. Focus on making Phase B results crystal clear before starting Phase C robustness tests.
