# Conclusion

We built a pragmatic, reproducible KG+ML system that preserves meaning and runs fast. The results show you can get both: solid semantic fidelity (SRS=0.7571) and sub‑millisecond retrieval (0.037ms p99) on a realistic corpus. The classification baseline is near‑perfect with concept features (99.68% micro‑F1); the +3pp improvement gate should be reconsidered when baselines are already high.

## What we learned
- Structure matters. Auto‑taxonomy lifted SRS by fixing hierarchy coverage.
- Simpler is better. The consistency penalty reduced macro‑F1; keep λ=0.0.
- Deterministic metrics are powerful. HP/AtP/AP yield stable, reproducible SRS.
- Sklearn is a strong production default. PyTorch adds flexibility for research.

## Why it matters
- Teams can deploy hybrid retrieval with confidence and measure semantic fidelity, not just accuracy.
- Concept features are a lightweight way to inject graph signal into text models.

## What we’d do next
1. Implement RTF (embedding‑based) and test stability across seeds
2. Package the sklearn baseline as a service with post‑hoc hierarchy fixes
3. Scale graph‑filtered retrieval and add more datasets
4. Expand and audit taxonomy with human‑in‑the‑loop curation
