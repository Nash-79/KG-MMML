# System Architecture

## Overview
Hybrid graph–vector pipeline for SEC EDGAR KG–MMML integration. Graph provides structure and governance; vector index provides fast candidate retrieval. Queries are filtered by KG constraints, then ranked by vector similarity.

**Production system (validated through M5)**: Scikit-learn text+concept baseline (TF-IDF + one-hot concept features, λ=0.0). Simple, fast, stable, and effective (99.68% micro-F1, 0.7571 SRS, 0.037ms p99 latency).

## Components
1. **Data Layer** — SEC CompanyFacts → normalised `facts.jsonl` (namespace-aware concepts).
2. **KG Layer** — Snapshot as Neo4j/RDF-compatible CSV (nodes/edges), with `is-a` (auto + manual) for hierarchy.
3. **Feature Layer** — TF-IDF text + **one-hot concept features** (production); optional KG embeddings (research).
4. **Retrieval Layer (ANN)** — **Annoy (SVD-256)** with 20 trees (production); FAISS HNSW for future comparison.

## Data Flow
Facts → (normalise) → `facts.jsonl` → (build KG + taxonomy union) → snapshot → (extract features) → text+concept baseline → predictions + SRS monitoring → latency harness (ANN + exact/filtered cosine).

## Production Deployment (M5 Validated)

**Model**: Scikit-learn LogisticRegression
**Features**: TF-IDF (text) + binary concept indicators (one-hot)
**Training**: `--random_state 42`, `--test_size 0.25`, stratified splits
**Performance**:
- Micro-F1: 99.68%
- Macro-F1: 81.28% (+2.27pp over text-only)
- SRS: 0.7571 (HP=0.2726, AtP=0.9987, AP=1.0)
- Latency p99: 0.048ms at N=3,218

**Why this works**:
- Concept features capture hierarchy through co-occurrence
- Simple model is more stable than joint objectives with penalties
- Sub-millisecond latency at realistic scale (10³–10⁴)

## Design Decisions

### Validated (Phase B Complete)
- **Why text baseline first?** Establishes a lower bound before KG integration and protects against illusory gains. Confirmed: baseline at 98.32% sets honest comparison point.
- **Why concept one-hot vs embeddings?** Interpretable, cheap, and sufficient. Confirmed: delivers 99.68% micro-F1 without embedding complexity.
- **Why ANN?** Sub-millisecond p95 at N≈10³–10⁴ with tight p99. Confirmed: 0.037ms p99 at N=3,218, well below 150ms target.
- **Why λ=0.0 (no penalty)?** M5 tested consistency penalty on directional edges. Result: penalties hurt performance and training stability. Simple model wins.

### Planned (Phase C-D)
- **Hybrid pre-filters:** KG pre-filters should shrink candidate sets before cosine ranking. To be validated in M8 scalability tests.
- **Two-hop queries:** Test graph traversal + vector ranking. Planned for M8.
- **Domain vs generic KG:** Compare SEC-specific taxonomy vs generic knowledge graphs. Planned for M8.

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

**Interpretation.** At N≈10³–10⁴, **ANN** dominates exact cosine, and **filtered-cosine** demonstrates the hybrid benefit (p95 falls with small candidate sets).

**Status**: Latency targets validated (p99 = 0.048ms << 150ms target). Production deployment uses Annoy. FAISS HNSW parity and N=10,000 scaling planned for M8 (W15-16).

