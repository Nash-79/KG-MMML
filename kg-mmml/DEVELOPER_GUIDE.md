# Developer Guide

This guide provides technical documentation for the KG-MMML hybrid knowledge graph and machine learning system.

## Project Overview

MSc research project (CSC40098, Keele University) investigating knowledge graph integration with machine learning for SEC financial document classification while preserving semantic structure and meeting performance requirements.

The central research question asks whether we can retain the benefits of knowledge graphs (hierarchy, relations, explainability) without sacrificing retrieval speed or losing semantic meaning during vector compression. The literature review identified that pure vector models lose relational structure while pure graph queries are slow. This hybrid approach uses graphs for semantics and vector indices for speed.

## Current Status (Week 11-12)

M6 consolidation milestone complete. M7 robustness testing scripts implemented and ready for execution.

Decision gate results:
- SRS = 0.7571 (target ≥0.75) - PASS
- Latency p99 = 0.037ms (target <150ms) - PASS
- +3pp micro-F1 improvement = +1.36pp (target ≥3.0pp) - FAIL

M5 experiments showed that consistency penalty (λ > 0) does not improve performance. The simpler λ=0.0 model performs better. The +3pp micro-F1 gate appears too strict at 99.68% baseline accuracy due to ceiling effects.

## Setup and Installation

### Initial Setup
```bash
make setup              # Creates .env, directories
make install-dev        # Install with dev dependencies
```

### Running Experiments
```bash
# Text-only baseline
python -m src.cli.baseline_tfidf \
  --facts data/processed/sec_edgar/facts.jsonl \
  --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
  --out reports/tables/baseline_text_seed42_metrics.json \
  --random_state 42 --test_size 0.25

# Text + concept features (joint)
python -m src.cli.train_joint \
  --facts data/processed/sec_edgar/facts.jsonl \
  --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
  --concept_npz data/processed/sec_edgar/features/concept_features_filing.npz \
  --concept_index data/processed/sec_edgar/features/concept_features_index.csv \
  --consistency_weight 0.0 --epochs 20 --batch 128 --seed 42 \
  --out outputs/joint_with_concepts/metrics.json

# Build taxonomy (auto-generation via regex + frequency rules)
python -m src.cli.build_taxonomy \
  --facts data/processed/sec_edgar/facts.jsonl \
  --manual datasets/sec_edgar/taxonomy/usgaap_min.csv \
  --rules datasets/sec_edgar/taxonomy/pattern_rules.yaml \
  --out datasets/sec_edgar/taxonomy/usgaap_combined.csv \
  --min_cik_support 3 --with_closure

# Evaluate latency
python -m src.cli.evaluate_latency \
  --facts data/processed/sec_edgar/facts.jsonl \
  --method annoy --n_trees 20 --n_dims 256

# Compute SRS
python -m src.cli.compute_srs \
  --snapshot data/kg/sec_edgar_snapshot/ \
  --taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv
```

### Testing
```bash
make test               # Run all tests
make test-cov           # Tests with coverage report
pytest tests/ -v -m unit              # Unit tests only
pytest tests/ -v -m integration       # Integration tests only
```

### Code Quality
```bash
make lint               # Check style (black, isort, flake8)
make format             # Format code
make clean              # Remove build artifacts
```

## Data Pipeline

```
SEC EDGAR CompanyFacts (JSON)
  → normalize → facts.jsonl (namespace-aware: us-gaap:Revenue, dei:EntityCIK, etc.)
  → build_taxonomy → taxonomy CSV (child,parent relationships with transitive closure)
  → make_concept_features → concept_features.npz (binary indicators, one-hot style)
  → train (baseline or joint) → model + metrics.json
  → evaluate_latency → p50/p95/p99 latency reports
```

## System Components

### Data Layer (data/)
- facts.jsonl: Normalized SEC filings (cik, ns, concept, unit, period, value)
- Free data from SEC EDGAR CompanyFacts API

### Knowledge Graph Layer (datasets/sec_edgar/taxonomy/)
- Taxonomy builder merges: manual seed + regex pattern rules + frequency rules + backbone
- Output: child,parent CSV with optional transitive closure
- Example: AccountsReceivable → CurrentAssets → Assets

### Feature Layer
- Text features: TF-IDF on concept labels (baseline)
- Concept features: Binary indicators for KG-as-features
- Stored as sparse .npz matrices

### Retrieval Layer (src/cli/evaluate_latency.py)
- Annoy (20 trees, SVD-256): Current default
- FAISS HNSW: Planned for comparison
- Filtered cosine: Hybrid KG pre-filter + vector ranking

### CLI Tools (src/cli/)
- Standalone pipeline stages
- Run with `python -m src.cli.<script_name> --help`

## Metrics

### Semantic Retention Score (SRS)
Composite metric for knowledge preservation:
- HP (Hierarchy Presence): % concepts with parent via is-a (weight 0.25)
- AtP (Attribute Predictability): % concepts with unit edges (weight 0.20)
- AP (Asymmetry Preservation): No erroneous reverse edges (weight 0.20)
- RTF (Relation Type Fidelity): Reserved for future (weight 0.35)

Formula: SRS = 0.25×HP + 0.20×AtP + 0.20×AP + 0.35×RTF

### Classification Metrics
- Macro-F1: Tracks rare classes
- Micro-F1: Overall accuracy weighted by support

### Latency Metrics
- p50/p95/p99 percentiles (not just mean)

## Implementation Patterns

### Taxonomy Building
Multi-source strategy:
- Manual CSV: Seed taxonomy with core relationships
- Pattern rules: YAML regex patterns (e.g., ".*Receivable.*" → CurrentAssets)
- Frequency rules: Common concept families with CIK support thresholds
- Backbone: Hardcoded structural relationships
- Transitive closure: Materializes all ancestor paths

### Namespace Handling
Concepts use full namespace (us-gaap:Revenue). The system normalizes to ns:concept format and defaults to us-gaap: when not specified. See build_taxonomy.py::normalize_df() for implementation.

### Two-Stage Evaluation
Critical for validity:
1. Text-only baseline establishes lower bound
2. Joint model must show +3pp micro-F1 improvement

This prevents illusory gains from architecture changes.

### Reproducibility Requirements
- Fixed random seeds (--random_state 42)
- Stratified splits (--test_size 0.25)
- Pinned data snapshots in configs/
- Deterministic SRS components (HP/AtP/AP)

### Latency Measurement
- Warmed caches (first query excluded)
- Pinned threads (CPU affinity when possible)
- 500+ query runs for stable percentiles
- Report p50/p95/p99, not just mean

## Configuration Files

Experiments defined in configs/:
- experiment_baseline.yaml: Text-only TF-IDF
- experiment_joint.yaml: Text + concept features
- experiment_kge.yaml: KG embedding experiments

## Common Development Tasks

### Adding concept pattern rules
1. Edit datasets/sec_edgar/taxonomy/pattern_rules.yaml
2. Add regex under appropriate parent
3. Rebuild: `python -m src.cli.build_taxonomy ...`

### Running single tests
```bash
pytest tests/test_taxonomy.py -v
```

### Debugging failed experiments
1. Check logs/ for traces
2. Inspect outputs/<experiment>/ for intermediate results
3. Verify data paths in config YAML
4. Confirm .env has SEC User-Agent

### Comparing experiment runs
```bash
python scripts/compare_comprehensive.py \
  --baseline reports/tables/baseline_metrics.json \
  --joint outputs/joint_experiment/metrics.json \
  --output reports/tables/comparison.csv
```

## Directory Structure

- data/processed/sec_edgar/: Normalized facts and features (git-ignored)
- data/kg/: KG snapshots (git-ignored)
- datasets/sec_edgar/: Static taxonomy resources (committed)
- outputs/: Experiment outputs (git-ignored)
- reports/: Final tables and figures (committed)
- logs/: Runtime logs (git-ignored)

## Documentation

- docs/01_METHODOLOGY.md: System design and metric definitions
- docs/02_RESULTS_NARRATIVE.md: Experimental findings
- docs/03_CONCLUSION.md: Summary and future work
- docs/Architecture.md: Component details and design decisions
- docs/progress/: Weekly progress logs

## Design Rationale

### SEC EDGAR Data Source
Free data with real-world complexity, namespace-aware concepts, and no licensing barriers.

### Text Baseline Requirement
Establishes lower bound and prevents claiming KG benefits when gains come from architecture changes.

### Auto-Taxonomy Generation
Manual curation doesn't scale. Regex and frequency rules provide conservative, explainable hierarchy generation.

### Hybrid Architecture Choice
Graphs preserve semantics while vector indices deliver speed. Specialization beats monolithic stores at scale.

### SRS Metric Development
Accuracy alone hides semantic loss. Quantifiable measures needed to prove KG contribution beyond label co-occurrence.

## Code Style

- Python 3.10+ required
- Line length: 100 characters (black + isort configured)
- Type hints encouraged but not enforced
- Imports: isort profile=black
- Tests marked as unit/integration/slow

## Integration Patterns

This implementation validates findings from the literature review identifying three integration patterns:

1. KG-as-Features: Pre-computed embeddings (fast but loses structure)
2. Joint KG-MM Objectives: Shared space with constraints (better fidelity, heavier training)
3. Retrieval-time Routing: Hybrid architecture (production-ready, operational)

The hybrid approach (graph for structure + vector for speed) preserves semantics while meeting realistic performance targets.

