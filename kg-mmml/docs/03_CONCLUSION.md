# Conclusion

I built a pragmatic, reproducible KG+ML system that preserves meaning and runs fast. The results show you can get both: solid semantic fidelity (SRS=0.7571) and sub‑millisecond retrieval (0.037ms p99) on a realistic corpus. The classification baseline is near‑perfect with concept features (99.68% micro‑F1); the +3pp improvement gate should be reconsidered when baselines are already high.

## What I learned (Phase B: W5-10)
- Structure matters. Auto‑taxonomy lifted SRS by fixing hierarchy coverage (HP: 0% → 27.26%).
- Simpler is better. M5 tested consistency penalty (λ>0) on directional edges; result: penalties hurt performance and training stability. Production choice: λ=0.0. See [M5_COMPLETE.md](M5_COMPLETE.md).
- Deterministic metrics are powerful. HP/AtP/AP yield stable, reproducible SRS (σ=0.000).
- Sklearn is a strong production default. PyTorch adds flexibility for research but sklearn delivers better out-of-box performance (99.68% micro-F1).
- Macro-F1 matters. The +1.36pp micro-F1 improvement missed the gate, but +2.27pp macro-F1 shows concept features help rare classes where it matters most.

## Why it matters
- Teams can deploy hybrid retrieval with confidence and measure semantic fidelity, not just accuracy.
- Concept features are a lightweight way to inject graph signal into text models.
- Research framework (SRS metric, hybrid architecture, honest evaluation) is portable to other domains.

## What's next (Phase C-D: W11-24)
1. **M6 (W11-12)**: Consolidate metrics, prepare for robustness tests
2. **M7 (W13-14)**: Robustness testing (taxonomy off, unit noise, verify ≤10% drop)
3. **M8 (W15-16)**: Scalability exploration (two-hop+vector, domain vs generic KG)
4. **M9 (W17-18)**: Error analysis on 0.32% misclassifications, draft Results & Discussion
5. **M10-M12 (W19-24)**: Statistical validation (≥5 seeds), conclusions, video demo, submission

## Production deployment recommendation
- **Model**: sklearn LogisticRegression with TF-IDF + one-hot concept features
- **Config**: `random_state=42`, `test_size=0.25`, `consistency_weight=0.0`
- **Performance**: 99.68% micro-F1, 81.28% macro-F1, 0.7571 SRS, 0.048ms p99 latency
- **Why**: Simple, fast, stable, and effective. No PyTorch complexity needed.
