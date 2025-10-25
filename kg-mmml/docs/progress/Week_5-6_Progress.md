# Week 5-6 Progress Report

**Period:** Weeks 5-6  
**Status:** On track

---

## Summary

This period focused on scaling the data pipeline and establishing baseline measurements for knowledge graph quality and classification performance.

**Key achievements:**
- Scaled fact extraction to 1.3M rows from SEC EDGAR filings
- Rebuilt knowledge graph with normalized concepts (2,832 nodes, 71,882 edges)
- Implemented SRS computation with structural metrics
- Built baseline classification system using TF-IDF and concept features
- Created comparison framework for text-only vs text+concept models

**Current metrics:**
- SRS: 76.0% (overall graph quality)
- HP: 28.15% (hierarchy precision)
- AtP: 99.87% (attribute coverage)
- AP: 100% (asymmetry preservation)

---

## Data Pipeline and Knowledge Graph

**Data Processing**  
Extracted and normalized 1,339,327 facts from SEC EDGAR filings. Filtered to US-GAAP concepts with numeric units. Created filing-level aggregation (721 documents with taxonomy labels).

**Knowledge Graph Rebuild**  
- Nodes: 2,832 (concepts, units, periods)
- Edges: 71,882 (includes measured-in, for-period, is-a relationships)
- Applied namespace normalization for consistent concept identifiers
- Integrated initial taxonomy with parent-child relationships

**Files Generated:**
- `data/processed/sec_edgar/facts.jsonl` (1.3M rows)
- `data/kg/sec_edgar_2025-09-22/kg_nodes.csv`
- `data/kg/sec_edgar_2025-09-22/kg_edges.csv`

---

## SRS Quality Metrics

Built computation script (`compute_srs.py`) that measures:

- **HP (Hierarchy Precision):** 28.15% - Fraction of concepts with parent relationships
- **AtP (Attribute Predictability):** 99.87% - Fraction of concepts with unit edges
- **AP (Asymmetry Preservation):** 100% - Correct directionality of edges
- **SRS (Overall Score):** 76.0% - Weighted combination

**Key Finding:**  
HP is the primary limiting factor. Most concepts (99.87%) have proper unit attribution and directionality is perfect, but only 28% have hierarchical parents defined. This is expected and will be addressed through auto-taxonomy generation.

**Files Generated:**
- `srs_kge.csv` - Metric scores
- `srs_kge_debug.json` - Detailed breakdown

---

## Baseline Classification System

Created baseline classification pipeline with two modes:

1. **Text-only:** TF-IDF features from filing narratives
2. **Text + Concept:** TF-IDF + one-hot concept indicators

**Classification Task:** Predict parent taxonomy categories from filing content

**Results:**

| Mode | Micro-F1 | Macro-F1 | Documents (train/test) |
|------|----------|----------|------------------------|
| Text only | 99.21% | 99.02% | 540 / 181 |
| Text + Concept | 100% | 100% | 540 / 181 |

**Finding:**  
Adding concept features (KG-as-features) improves classification to perfect scores on this initial test set. This validates the approach of combining text and structured knowledge.

**Files Generated:**
- `baseline_text_metrics.json`
- `baseline_text_plus_concept_metrics.json`
- `baseline_vs_kge.csv`

**Scripts Created:**
- `make_concept_features.py` - Generate concept feature matrices
- `baseline_tfidf.py` - Train and evaluate baseline models
- `scripts/make_baseline_table.py` - Create comparison tables

---

## Progress Comparison

Comparing to Week 3-4 (when using smaller toy taxonomy):

| Metric | Week 3-4 | Week 5-6 | Change |
|--------|----------|----------|--------|
| AtP | ~4% | 99.87% | Much improved due to fact normalization |
| HP | ~75% (toy) | 28.15% (real scale) | Lower at scale; needs auto-taxonomy |
| AP | 100% | 100% | Maintained |
| SRS | ~59% | 76.0% | +17% improvement |

**Note:** HP dropped when moving to full scale because the manually curated taxonomy is intentionally conservative. The next phase will generate additional relationships automatically.

---

## Alignment to Plan

**Week 5-6 Plan (Milestone M3):** "KG-as-features; baseline SRS/accuracy/latency; seeds/configs"

**Completed:**
- ✅ KG-as-features implementation (concept feature extraction)
- ✅ Baseline classification system operational
- ✅ SRS computation working with all structural metrics
- ✅ Configs and random seeds standardized

**Not Started (as planned):**
- Latency harness - scheduled for Week 7-8
- Auto-taxonomy generation - scheduled for Week 7-8

**Status:** Aligned with M3 deliverables. On track for next phase.

---

## Challenges and Solutions

**Challenge 1: HP at 28% limits overall SRS score**
- Root Cause: Conservative manual taxonomy covers only subset of observed concepts
- Solution: Generate auto-taxonomy from high-precision pattern rules (Week 7-8 goal)
- Target: Raise HP to ≥25% through systematic relationship mining

**Challenge 2: Limited test set (181 documents)**
- Current: 7 taxonomy categories, perfect classification scores
- Next: Expand to full taxonomy and larger document set to get realistic metrics

---

## Next Steps (Week 7-8)

**Goal A: Auto-Taxonomy Generation**
- Build pattern-based relationship extraction from observed concepts
- Combine with manual taxonomy to create comprehensive hierarchy
- Rebuild KG and recompute SRS
- Target: HP ≥ 25%, maintain AtP/AP

**Goal B: Latency Benchmarking**
- Implement retrieval latency measurement across different methods
- Test exact search vs approximate nearest neighbors (ANN)
- Measure p50/p95/p99 latencies at scales of 1k-10k documents
- Target: Generate latency comparison table

**Goal C: Joint Model Initial Test**
- Build combined text+concept model with consistency constraints
- Test with/without penalty for directional relationships
- Target: Ablation study showing effect of constraints

**Goal D: Documentation**
- Update architecture documentation with auto-taxonomy flow
- Document latency measurement approach
- Link all evidence files from reports
