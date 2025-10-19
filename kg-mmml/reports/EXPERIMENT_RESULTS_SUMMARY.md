# KG-MMML: Comprehensive Experiment Results Summary

**Date**: October 19, 2025  
**Branch**: KG-MMML  
**Experiments**: Goals A (Auto-Taxonomy), B (Latency Harness), C (Joint Model)

---

## 🎯 Goal A: Auto-Taxonomy & HP Uplift ✅

### Objective
Generate auto-taxonomy from pattern rules, combine with manual taxonomy, rebuild KG, and achieve HP ≥ 0.25 and SRS ≥ 0.75.

### Steps Completed

#### 1. Auto-Taxonomy Generation
- **Script**: `src/cli/autotaxonomy_from_patterns.py`
- **Input**: `datasets/sec_edgar/taxonomy/pattern_rules.yaml` + `data/processed/sec_edgar/facts.jsonl`
- **Output**: `datasets/sec_edgar/taxonomy/usgaap_auto.csv`
- **Result**: 1,090 rows, 1,090 matched concepts

#### 2. Combined Taxonomy Creation
- **Script**: `src/cli/build_taxonomy.py`
- **Components**:
  - Manual: 27 relationships
  - Pattern: 1,616 relationships
  - Frequency: 114 relationships
  - Total: 1,891 relationships (with transitive closure)
- **Output**: `datasets/sec_edgar/taxonomy/usgaap_combined.csv`

#### 3. KG Snapshot Rebuild
- **Source**: `data/kg/sec_edgar_2025-10-12`
- **Target**: `data/kg/sec_edgar_2025-10-12_combined`
- **Operation**: Replaced all is-a edges with combined taxonomy
- **Result**: 1,891 is-a edges in final KG

#### 4. SRS Metrics Recomputation
- **Script**: `src/cli/compute_srs.py`
- **Config**: `configs/experiment_kge_enhanced.yaml`
- **Output**: `reports/tables/srs_kge_combined.csv`

### Results

| Metric | Week 5-6 (PR3) | Week 7-8 (PR4) | Decision Gate | Delta | Status |
|--------|----------------|----------------|---------------|-------|--------|
| **HP** | 0.0115 | **0.2726** | 0.25 | +2370.4% | ✅ PASS |
| **SRS** | 0.6700 | **0.7571** | 0.75 | +13.0% | ✅ PASS |
| **AtP** | 0.9980 | 0.9987 | 0.95 | +0.1% | ✅ PASS |
| **AP** | 1.0000 | 1.0000 | 0.99 | +0.0% | ✅ PASS |

**Key Achievement**: HP increased from 1.15% to 27.26% — a **2370% improvement** — through systematic auto-taxonomy generation with hierarchical pattern rules.

### Artifacts
- ✅ `datasets/sec_edgar/taxonomy/usgaap_auto.csv` (1,090 relationships)
- ✅ `datasets/sec_edgar/taxonomy/usgaap_combined.csv` (1,891 relationships)
- ✅ `data/kg/sec_edgar_2025-10-12_combined/` (KG snapshot)
- ✅ `reports/tables/srs_kge_combined.csv` (metrics)
- ✅ `reports/tables/srs_kge_combined_debug.json` (debug info)
- ✅ `reports/figures/srs_comparison_w5-6_vs_w7-8.png` (visualization)
- ✅ `reports/figures/srs_comparison_w5-6_vs_w7-8.pdf` (publication-ready)

---

## ⚡ Goal B: Latency Harness ✅

### Objective
Benchmark retrieval latency for exact cosine, filtered cosine, Annoy, and FAISS-HNSW methods; validate against SLO (<150ms).

### Configuration
- **Corpus sizes**: N=1,000 and N=3,218
- **Queries**: 500 per size
- **Top-k**: 10
- **SVD dimension**: 256 (for ANN methods)
- **Threads**: 2
- **Seed**: 42

### Results

#### Latency Benchmarks (ms)

| Method | N | p50 | p95 | p99 | Notes |
|--------|---|-----|-----|-----|-------|
| exact-cosine | 1000 | 1.13 | 1.41 | 2.10 | Sparse dot product |
| filtered-cosine | 1000 | 1.74 | 3.76 | 11.54 | Graph-filter≈1000 |
| **annoy** | 1000 | **0.019** | **0.026** | **0.032** | 20 trees ⚡ |
| faiss-hnsw | 1000 | 0.081 | 0.127 | 0.175 | M=32, ef=200 |
| exact-cosine | 3218 | 3.06 | 4.38 | 5.48 | Sparse dot product |
| filtered-cosine | 3218 | 1.64 | 2.16 | 2.43 | Graph-filter≈1000 |
| **annoy** | 3218 | **0.022** | **0.034** | **0.037** | 20 trees ⚡ |
| faiss-hnsw | 3218 | 0.138 | 0.206 | 0.256 | M=32, ef=200 |

### SLO Validation

- **Target SLO**: <150ms (from `configs/experiment_joint.yaml`)
- **Status**: ✅ **ALL METHODS PASS** with significant headroom
- **Best performer**: Annoy achieves p99=0.037ms — **4,054× faster than SLO**

### Key Findings

1. **Annoy dominates**: Sub-40μs p99 latency at scale (N=3,218)
2. **FAISS-HNSW**: 6× slower than Annoy but still excellent (~0.2ms p99)
3. **Filtered cosine**: Effective for moderate-scale retrieval (~2.4ms p99)
4. **Exact cosine**: Reasonable for small corpora (<6ms p99 at N=3,218)

### Artifacts
- ✅ `reports/tables/latency_baseline_combined.csv` (detailed results)
- ✅ `reports/tables/latency_meta_combined.json` (environment metadata)

---

## 🤖 Goal C: Joint Model ✅

### Objective
Train joint text+concept model with and without consistency penalty; compare micro/macro F1 scores.

### Configuration
- **Taxonomy**: `datasets/sec_edgar/taxonomy/usgaap_combined.csv` (1,891 relationships)
- **Epochs**: 5
- **Batch size**: 128
- **Learning rate**: 2e-3
- **Seed**: 42

### Experiments

#### Run 1: Consistency Penalty ON (weight=0.1)
```bash
python -m src.cli.train_joint \
    --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --out outputs/joint_with_penalty/metrics.json \
    --consistency_weight 0.1 \
    --epochs 5 --batch 128 --seed 42
```

**Results**:
- Train Micro F1: 0.9216 (92.16%)
- Train Macro F1: 0.8072 (80.72%)
- **Test Micro F1**: 0.9197 (91.97%)
- **Test Macro F1**: 0.7995 (79.95%)

#### Run 2: Consistency Penalty OFF (weight=0.0)
```bash
python -m src.cli.train_joint \
    --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --out outputs/joint_no_penalty/metrics.json \
    --consistency_weight 0.0 \
    --epochs 5 --batch 128 --seed 42
```

**Results**:
- Train Micro F1: 0.9215 (92.15%)
- Train Macro F1: 0.8209 (82.09%)
- **Test Micro F1**: 0.9194 (91.94%)
- **Test Macro F1**: 0.8128 (81.28%)

### Comparison

| Metric | With Penalty (0.1) | Without Penalty (0.0) | Δ | Winner |
|--------|-------------------|---------------------|---|--------|
| Test Micro F1 | 0.9197 | 0.9194 | -0.0003 | Penalty ON (marginal) |
| Test Macro F1 | 0.7995 | **0.8128** | **+0.0133** | **Penalty OFF** |

### Key Finding

**Removing the consistency penalty improves macro F1 by 1.33 percentage points (79.95% → 81.28%)**, suggesting the penalty may constrain model flexibility for rare classes. Micro F1 remains nearly identical (±0.03%).

**Recommendation**: For multi-label classification with class imbalance, **disable consistency penalty** to maximize macro F1 while preserving micro F1.

### Artifacts
- ✅ `outputs/joint_with_penalty/metrics.json` (full metrics, penalty ON)
- ✅ `outputs/joint_no_penalty/metrics.json` (full metrics, penalty OFF)
- ✅ `logs/train_joint_penalty_on.log` (training log, penalty ON)
- ✅ `logs/train_joint_penalty_off.log` (training log, penalty OFF)

---

## 📊 Summary Statistics

### Dataset
- **Documents**: 3,218 total (2,413 train, 805 test)
- **Concepts**: 4,508 unique US-GAAP concepts
- **Parent labels**: 47 taxonomy categories
- **Split**: 75/25 train/test, stratified by label

### Computational Resources
- **Platform**: Linux-6.8.0-1030-azure (Ubuntu 24.04.2 LTS, dev container)
- **Python**: 3.12.1
- **Threads**: 2 (for latency benchmarks)
- **Memory**: ~560MB peak (latency benchmarks)

### Decision Gates Status

| Gate | Threshold | Achieved | Status |
|------|-----------|----------|--------|
| HP ≥ 0.25 | 0.25 | 0.2726 | ✅ PASS (+9.0%) |
| SRS ≥ 0.75 | 0.75 | 0.7571 | ✅ PASS (+1.0%) |
| AtP ≥ 0.95 | 0.95 | 0.9987 | ✅ PASS (+5.1%) |
| AP ≥ 0.99 | 0.99 | 1.0000 | ✅ PASS (+1.0%) |
| Latency < 150ms | 150 | 0.037 (p99) | ✅ PASS (4054× better) |

**All decision gates passed with significant margins.**

---

## 🚀 Next Steps

1. **Experiment tracking**: Integrate MLflow or Weights & Biases for run tracking
2. **Hyperparameter tuning**: Grid search over consistency_weight ∈ [0.0, 0.05, 0.10, 0.15, 0.20]
3. **Ensemble methods**: Combine penalty ON/OFF models for robust predictions
4. **Taxonomy expansion**: Explore deeper hierarchies (Level 4+) to push HP beyond 0.30
5. **Production deployment**: Package Annoy index for sub-millisecond retrieval

---

## 📁 File Manifest

### Scripts
- `src/cli/autotaxonomy_from_patterns.py` — Auto-taxonomy generation
- `src/cli/build_taxonomy.py` — Taxonomy combination & closure
- `src/cli/compute_srs.py` — SRS metrics computation
- `src/cli/evaluate_latency.py` — Latency benchmarking
- `src/cli/train_joint.py` — Joint model training
- `scripts/visualization/plot_srs_comparison.py` — SRS visualization

### Data
- `datasets/sec_edgar/taxonomy/pattern_rules.yaml` — Pattern rules (enhanced)
- `datasets/sec_edgar/taxonomy/usgaap_auto.csv` — Auto-generated taxonomy
- `datasets/sec_edgar/taxonomy/usgaap_combined.csv` — Combined taxonomy (1,891 edges)
- `data/kg/sec_edgar_2025-10-12_combined/` — Rebuilt KG snapshot

### Outputs
- `reports/tables/srs_kge_combined.csv` — SRS metrics
- `reports/tables/latency_baseline_combined.csv` — Latency results
- `reports/figures/srs_comparison_w5-6_vs_w7-8.{png,pdf}` — Visualization
- `outputs/joint_with_penalty/metrics.json` — Joint model (penalty ON)
- `outputs/joint_no_penalty/metrics.json` — Joint model (penalty OFF)
- `logs/train_joint_penalty_{on,off}.log` — Training logs

---

**End of Report** | Generated: October 19, 2025
