# KG‑MMML: Hybrid Knowledge Graph + ML

This project builds a system that retrieves SEC financial documents and classifies them using both knowledge graphs and machine learning. Embeddings alone lose graph structure; pure graph queries are slow. We combine both: the graph for meaning, a vector index for speed.

## Quick results

| Gate | Target | Actual | Status |
|------|--------|--------|--------|
| SRS (overall) | ≥0.75 | 0.7571 | ✅ PASS |
| Latency p99 | <150ms | 0.037ms | ✅ PASS |
| +3pp micro‑F1 | ≥+3.0pp | +1.36pp | ❌ FAIL |

Notes: Concept features deliver near‑perfect accuracy (99.68% micro‑F1) and +2.27pp macro‑F1, but the +3pp micro‑F1 threshold was too strict at this performance level.

**M5 Complete (Week 9-10)**: Joint objective with consistency penalty tested. Result: λ=0.0 (no penalty) outperforms constrained variants. Simple sklearn baseline is production choice. See [docs/M5_COMPLETE.md](docs/M5_COMPLETE.md).

## Reproduce Week 9

```bash
# Baseline (text‑only)
python -m src.cli.baseline_tfidf \
	--facts data/processed/sec_edgar/facts.jsonl \
	--taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
	--out reports/tables/baseline_text_seed42_metrics.json \
	--random_state 42 --test_size 0.25

# Joint (text + concept features, λ=0.0)
python -m src.cli.train_joint \
	--facts data/processed/sec_edgar/facts.jsonl \
	--taxonomy datasets/sec_edgar/taxonomy/usgaap_combined.csv \
	--concept_npz data/processed/sec_edgar/features/concept_features_filing.npz \
	--concept_index data/processed/sec_edgar/features/concept_features_index.csv \
	--consistency_weight 0.0 --epochs 20 --batch 128 --seed 42 \
	--out outputs/joint_with_concepts_no_penalty_e20/metrics.json

# Compare
python scripts/compare_comprehensive.py \
	--output reports/tables/baseline_vs_joint_comprehensive_w9.csv
```


## Project structure

```
src/cli/           - Main scripts (taxonomy, features, training, eval)
configs/           - Final experiment configs
datasets/          - SEC EDGAR taxonomy and helpers
data/              - Generated data & KG snapshots (git‑ignored)
reports/           - Results CSVs and figures
docs/              - Methodology and results
tests/             - Automated tests
```

## Docs
- docs/01_METHODOLOGY.md
- docs/02_WEEK7-8_RESULTS.md
- docs/03_WEEK9_RESULTS.md
- docs/04_RESULTS_NARRATIVE.md
- docs/05_CONCLUSION.md
