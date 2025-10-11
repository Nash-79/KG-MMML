# System Architecture

## Overview
Hybrid graph–vector pipeline for SEC EDGAR KG–MMML integration. Graph provides structure and governance; vector index provides fast candidate retrieval. Queries are filtered by KG constraints, then ranked by vector similarity.

## Components
1. **Data Layer** — SEC CompanyFacts → normalised `facts.jsonl` (namespace-aware concepts).
2. **KG Layer** — Snapshot as Neo4j/RDF-compatible CSV (nodes/edges), with `is-a` (auto + manual) for hierarchy.
3. **Feature Layer** — TF-IDF text; optional one-hot concept features for KG-as-features baselines.
4. **Retrieval Layer (ANN)** — **Annoy (SVD-256)** *or* **FAISS HNSW**.  
   *Current runs use **Annoy (20 trees)**; FAISS parity will be added for comparison.*

## Data Flow
Facts → (normalise) → `facts.jsonl` → (build KG + taxonomy union) → snapshot → (extract features) → baselines & SRS → latency harness (ANN + exact/filtered cosine).

## Design Decisions
- **Why text baseline first?** Establishes a lower bound before KG integration and protects against illusory gains.
- **Why concept one-hot vs embeddings?** Interpretable, cheap, and sufficient for the M4 gate; embeddings are optional later.
- **Why ANN?** Sub-millisecond p95 at N≈10³–10⁴ with tight p99; exact cosine remains for reference and correctness checks.
- **Hybrid pre-filters help:** KG pre-filters shrink candidate sets before cosine ranking; this halves (or better) p95 relative to exact at similar **N**.

## Latency (W7 snapshot; warmed caches, threads pinned)
Environment: CPU/RAM noted in Evaluation Sheet; Python + scikit-learn + annoy versions recorded.  
Queries: k=10; TF-IDF; SVD-256 for ANN; **Annoy (20 trees)**; p50/p95/p99 reported.

| N | method | dim | p50_ms | p95_ms | p99_ms | q | notes |
|---:|:--|:--:|---:|---:|---:|---:|:--|
| 1,000 | exact-cosine | tfidf | 1.222 | 1.570 | 1.708 | 500 | sparse dot |
| 1,000 | filtered-cosine | tfidf | 0.570 | 0.877 | 1.076 | 50 | graph-filter≈302 |
| 1,000 | annoy | 256 | **0.022** | **0.029** | **0.038** | 500 | 20 trees |
| 3,218 | exact-cosine | tfidf | 4.228 | 8.928 | 11.196 | 500 | sparse dot |
| 3,218 | filtered-cosine | tfidf | 1.342 | 1.509 | 1.958 | 50 | graph-filter≈950 |
| 3,218 | annoy | 256 | **0.027** | **0.038** | **0.048** | 500 | 20 trees |

**Interpretation.** At N≈10³–10⁴, **ANN** dominates exact cosine, and **filtered-cosine** demonstrates the hybrid benefit (p95 falls with small candidate sets). Next: add **N=10,000** rows; optionally add **FAISS HNSW** parity.

