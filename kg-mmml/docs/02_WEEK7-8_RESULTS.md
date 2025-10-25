# Week 7-8 Results

Status: ✅ All gates passed (HP, AtP, AP, SRS, latency)

## Auto‑Taxonomy
- Built pattern‑based rules (plus frequency) over 1,090 concepts
- Final taxonomy = 1,891 parent‑child relations (27 manual, 1,616 patterns, 114 frequency)

Metrics impact:
- HP: 0.2815 → 0.2726 (maintained; ≥0.25 gate PASS)
- SRS: 0.7600 → 0.7571 (maintained; ≥0.75 gate PASS)
- AtP: 0.9987 → 0.9987 (stable)
- AP: 1.0000 → 1.0000 (stable)

Evidence: `reports/tables/srs_kge_combined.csv`, `..._debug.json`

## Latency Benchmarks
- Methods: exact cosine, graph‑filtered cosine, Annoy, FAISS HNSW
- Sizes: 1k and 3,218 docs; 500 queries/config; p50/p95/p99 recorded

p99 results (ms):
- Annoy: 0.037 (best)
- FAISS HNSW: 0.256
- Graph‑filtered: 2.43
- Exact cosine: 5.48

Gate: p99 < 150ms → PASS (all methods)

Evidence: `reports/tables/latency_baseline_combined.csv`, `latency_meta_combined.json`

## Joint Model Ablation
- With penalty (λ=0.1): micro‑F1=91.97%, macro‑F1=79.95%
- Without penalty (λ=0.0): micro‑F1=91.94%, macro‑F1=81.28%
- Finding: penalty hurts macro‑F1 by 1.33pp
- Recommendation: default λ=0.0

Evidence: `outputs/joint_with_penalty/metrics.json`, `outputs/joint_no_penalty/metrics.json`
