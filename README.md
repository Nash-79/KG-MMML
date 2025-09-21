# Integrating Knowledge Graphs with Multi-Modal Machine Learning (KG-MMML)

**Goal:** A reproducible framework for fusing Knowledge Graphs (KGs) with Multi-Modal ML (MMML) that preserves semantics, scales operationally, and explains outputs for open-world retrieval & zero-shot classification.

## ✨ Features
- **Multi-resolution semantics** (types → relations → k-hop → paths)
- **Hybrid retrieval**: graph spine + vector index + cache + stream
- **Honest evaluation**: accuracy + SRS + p95/p99 latency + robustness + rationale precision
- **Reproducible runs** driven by YAML configs

## 🛠️ Quickstart
```bash
# 1) Setup
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e .         # uses pyproject.toml
# or: pip install -r requirements.txt

# 2) Baseline run
python -m src.cli.train --config configs/experiment_baseline.yaml

# 3) Compute SRS on a run
python -m src.cli.compute_srs --config configs/experiment_kge.yaml --out reports/tables/srs.csv

# 4) Evaluate latency (hybrid system)
python -m src.cli.evaluate_latency --config configs/system_hybrid.yaml --out reports/tables/latency.csv
