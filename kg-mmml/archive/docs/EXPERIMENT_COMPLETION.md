# Experiment Completion Summary

##  All Goals Achieved

### Goal A: Auto-Taxonomy & HP Uplift
-  Auto-taxonomy generated (1,090 concepts matched)
-  Combined taxonomy created (1,891 total relationships)
-  KG snapshot rebuilt with combined taxonomy
-  SRS recomputed: **HP=0.2726** (target ≥0.25), **SRS=0.7571** (target ≥0.75)
-  **HP improved by 2370%** from W5-6 to W7-8

### ⚡ Goal B: Latency Harness
-  Latency benchmarks completed for all methods
-  **Annoy achieves p99=0.037ms** (4054× faster than 150ms SLO)
-  All methods pass SLO with significant headroom
-  Results saved to `reports/tables/latency_baseline_combined.csv`

### 🤖 Goal C: Joint Model
-  Trained with consistency penalty ON (weight=0.1): Macro F1=0.7995
-  Trained with consistency penalty OFF (weight=0.0): Macro F1=0.8128
-  **Finding: Penalty OFF improves macro F1 by 1.33 percentage points**
-  Recommendation: Use `consistency_weight=0.0` for production

## 📊 Key Metrics

| Metric | Week 5-6 | Week 7-8 | Gate | Status |
|--------|----------|----------|------|--------|
| HP | 0.0115 | **0.2726** | 0.25 |  PASS |
| SRS | 0.6700 | **0.7571** | 0.75 |  PASS |
| AtP | 0.9980 | 0.9987 | 0.95 |  PASS |
| AP | 1.0000 | 1.0000 | 0.99 |  PASS |

**All decision gates passed.**

## 📁 Generated Artifacts

### Data & Taxonomy
- `datasets/sec_edgar/taxonomy/usgaap_auto.csv` (95K, 1,090 relationships)
- `datasets/sec_edgar/taxonomy/usgaap_combined.csv` (164K, 1,891 relationships)
- `data/kg/sec_edgar_2025-10-12_combined/` (KG snapshot with combined taxonomy)

### Results & Metrics
- `reports/tables/srs_kge_combined.csv` (SRS metrics)
- `reports/tables/srs_kge_combined_debug.json` (debug info)
- `reports/tables/latency_baseline_combined.csv` (latency benchmarks)
- `reports/tables/latency_meta_combined.json` (environment metadata)
- `outputs/joint_with_penalty/metrics.json` (joint model, penalty ON)
- `outputs/joint_no_penalty/metrics.json` (joint model, penalty OFF)

### Logs
- `logs/train_joint_penalty_on.log` (training log, consistency ON)
- `logs/train_joint_penalty_off.log` (training log, consistency OFF)

### Visualizations
- `reports/figures/srs_comparison_w5-6_vs_w7-8.png` (257K, SRS progression)
- `reports/figures/srs_comparison_w5-6_vs_w7-8.pdf` (29K, publication-ready)
- `reports/figures/joint_model_comparison.png` (joint model ablation)
- `reports/figures/joint_model_comparison.pdf` (publication-ready)

### Documentation
- `reports/EXPERIMENT_RESULTS_SUMMARY.md` (comprehensive report)
- `scripts/visualisation/plot_srs_comparison.py` (SRS visualisation script)
- `scripts/visualisation/plot_joint_comparison.py` (joint model visualisation script)

## Commands to Reproduce

### Goal A: Auto-Taxonomy
```bash
# Generate auto-taxonomy
python src/cli/autotaxonomy_from_patterns.py \
    --facts data/processed/sec_edgar/facts.jsonl \
    --rules datasets/sec_edgar/taxonomy/pattern_rules.yaml \
    --out datasets/sec_edgar/taxonomy/usgaap_auto.csv

# Combine taxonomies
python src/cli/build_taxonomy.py \
    --facts data/processed/sec_edgar/facts.jsonl \
    --manual datasets/sec_edgar/taxonomy/usgaap_min.csv \
    --rules datasets/sec_edgar/taxonomy/pattern_rules.yaml \
    --out datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --with_closure

# Rebuild KG and compute SRS
python src/cli/compute_srs.py \
    --config configs/experiment_kge_enhanced.yaml \
    --out reports/tables/srs_kge_combined.csv
```

### Goal B: Latency Harness
```bash
python -m src.cli.evaluate_latency \
    --facts data/processed/sec_edgar/facts.jsonl \
    --out reports/tables/latency_baseline_combined.csv \
    --meta_out reports/tables/latency_meta_combined.json \
    --sizes 1000 10000 --queries 500 --k 10 --svd_dim 256 \
    --filtered --use_annoy --use_faiss --threads 2
```

### Goal C: Joint Model
```bash
# With penalty
python -m src.cli.train_joint \
    --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --out outputs/joint_with_penalty/metrics.json \
    --consistency_weight 0.1 --epochs 5 --batch 128 --seed 42

# Without penalty
python -m src.cli.train_joint \
    --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --out outputs/joint_no_penalty/metrics.json \
    --consistency_weight 0.0 --epochs 5 --batch 128 --seed 42
```

### Visualizations
```bash
python scripts/visualisation/plot_srs_comparison.py
python scripts/visualisation/plot_joint_comparison.py
```

## Next Steps (Weeks 9-10): Phase B, Milestone M5

### Week 9 Goals (Oct 25-31, 2025) -  COMPLETED

#### Goal 1: Baseline F1 Validation
- [x]  Discovered critical issue: original joint model lacked concept features
- [x]  Generated concept features (4,502 concepts, binary indicators)
- [x]  Fixed baseline split logic to match joint model (stratified, seed=42)
- [x]  Reran text-only baseline: macro=97.23%, micro=98.33%
- [x]  Ran text+concept baseline: macro=99.50%, micro=99.68%
- [x]  Compared baseline vs joint models (5 configurations)
- [x] Decision gate FAILED: +1.36pp micro-F1 < 3pp threshold
- **Result**: Concept features improve macro-F1 by +2.27pp, micro-F1 by +1.36pp
- **Acceptance**:  `reports/tables/baseline_vs_joint_comprehensive_w9.csv`

#### Goal 2: Joint Model Refinement
- [x]  Documented consistency penalty trade-off analysis
- [x]  Updated `configs/experiment_joint.yaml` to λ=0.0 default
- [x]  Added detailed rationale comments in config
- [x] ⏭Optional λ sensitivity (0.01, 0.05) deferred to Week 10
- **Result**: Penalty decreases macro-F1 by -1.33pp without benefit
- **Acceptance**:  Updated config + comprehensive documentation in `EXPERIMENT_RESULTS_SUMMARY.md`

#### Goal 3: SRS Stability Check
- [x]  Analyzed SRS metric determinism (all structural metrics)
- [x]  Verified empirical stability across 2 independent runs (σ=0.000)
- [x]  Generated stability report with confidence intervals
- [x]  Decision gate PASSED: σ=0.000 < 0.05 threshold
- **Result**: Perfect stability for deterministic topology-based metrics
- **Acceptance**:  `reports/tables/srs_stability_w9.csv` + analysis in `EXPERIMENT_RESULTS_SUMMARY.md`

#### Week 9 Artifacts
-  `WEEK9_COMPLETION.md` - Comprehensive Week 9 summary report
-  `docs/WEEK9_PLAN.md` - Detailed execution plan
-  `data/processed/sec_edgar/features/concept_features_filing.npz` - 4,502 concepts
-  `reports/tables/baseline_text_seed42_metrics.json` - Text-only baseline
-  `reports/tables/baseline_text_plus_concept_seed42_metrics.json` - Text+concept baseline
-  `reports/tables/baseline_vs_joint_comprehensive_w9.csv` - 5-model comparison
-  `reports/tables/srs_stability_w9.csv` - Stability verification
-  `scripts/compare_comprehensive.py` - Multi-model comparison tool
-  `scripts/compute_srs_stability.py` - SRS stability checker

### Week 10 Goals (Nov 1-7, 2025) - Planned 📅
1. Hyperparameter optimisation (PyTorch training to match sklearn performance)
2. Feature engineering enhancements (concept embeddings, frequency weighting)
3. Production readiness (inference service, monitoring, post-hoc constraints)
4. RTF implementation (embedding-based relational fidelity metric)

**See detailed plans**: `docs/WEEK9_PLAN.md`, `WEEK9_COMPLETION.md`

---

## 📊 Historical Results (Weeks 5-8)

### Week 7-8 Completion Summary
- **Experiment Date**: October 19, 2025
- **Branch**: KG-MMML
- **Status**:  All goals completed successfully
- **Next Steps**: Execute Week 9 plan

### Previous Achievements
1.  **Merge to main**: All experiments validated (completed Oct 25, 2025)
2. MLflow integration: Track experiments systematically
3. Hyperparameter tuning: Grid search for optimal consistency_weight
4. Taxonomy expansion: Explore Level 4+ hierarchies
5. Deployment: Package Annoy index for production retrieval
