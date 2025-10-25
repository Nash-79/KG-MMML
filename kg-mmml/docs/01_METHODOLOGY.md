# Methodology

This project builds a hybrid system that retrieves SEC financial documents and classifies them using both knowledge graphs and machine learning. The key idea: embeddings alone lose important structure in the knowledge graph, while pure graph queries are slow. We combine both—graph for meaning, vector index for speed.

## Architecture (hybrid)
- Graph spine for semantic structure (concepts, units, periods, taxonomy edges)
- Text encoder (TF‑IDF) for fast lexical features
- Concept features (binary indicators) for KG‑as‑features
- Optional neural joint model (PyTorch) for research ablations
- Vector index for low‑latency retrieval (Annoy/FAISS)

## Data and pipelines
- Source: SEC EDGAR CompanyFacts JSON (fast, stable)
- Stages: fetch → normalize → build KG → compute metrics → train/eval
- Snapshots under `data/kg/sec_edgar_*` (pinned in configs)

## Metrics (beyond accuracy)
- HP (Hierarchy Presence): parent coverage in taxonomy
- AtP (Attribute Predictability): concepts with unit edges
- AP (Asymmetry Preservation): directional edges without reverse
- RTF (Relation Type Fidelity): embedding-based (future)
- SRS = 0.25*HP + 0.20*AtP + 0.20*AP + 0.35*RTF
- Classification: macro‑F1 (rare classes), micro‑F1 (overall)
- Latency: p50/p95/p99 (service objective p99 < 150ms)

## Decision gates
- SRS ≥ 0.75 (quality)
- HP ≥ 0.25, AtP ≥ 0.95, AP ≥ 0.99 (structure)
- +3pp micro‑F1: text+concept vs text‑only (added value)
- Latency p99 < 150ms (operational)

## Reproducibility
- Fixed seeds (42) and stratified splits (match across scripts)
- Pinned configs under `configs/` (paths, snapshots, hyperparameters)
- Deterministic SRS components (HP/AtP/AP) for stability

## Why this design
- Keep semantics: KG edges matter for meaning and explainability
- Keep speed: vector index delivers sub‑millisecond retrieval
- Keep honesty: report accuracy with SRS and latency together

## Risks and mitigations
- Sparse taxonomy → auto‑taxonomy rules (pattern+frequency)
- Small label support → stratified splits, macro‑F1 tracking
- Neural variance → prefer sklearn baseline for production
