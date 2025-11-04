# Working Notes

## Week 7-8 Breakthrough

Spent days trying to get HP above 0.10. Manual taxonomy curation was killing me - only had ~30 parent relations. Finally realized I could auto-generate is-a edges from concept names using regex patterns. 

Tried these patterns:
- `.*Receivable.*` → CurrentAssets
- `.*Payable.*` → CurrentLiabilities  
- `.*Revenue.*` → Revenues

Combined with frequency threshold (min_cik_support=3) to avoid spurious matches. HP jumped from basically zero to 27.26%. Massive lift.

## Week 9 - Consistency Penalty Experiment

Hypothesis: Adding λ penalty on directional edges would improve micro-F1 by enforcing hierarchy constraints.

Results: Nope. Model with λ=0.0 (no penalty) performs better. The penalty adds training complexity without helping classification. Suspect the concept features already capture hierarchy implicitly through co-occurrence patterns.

Lesson: Simpler is better. The baseline sklearn model is production-ready; the PyTorch joint model is research overhead without payoff.

## +3pp Gate Issue

This is frustrating. We're at 99.68% micro-F1 already. Asking for +3pp from that baseline is basically asking for perfection. The gate might be theoretically sound but practically too strict.

Need to discuss in M5 wrap-up: Is the gate threshold appropriate given we're hitting ceiling effects?

## Next: M10-11

- Robustness tests (taxonomy off, noisy units)
- Error analysis on the 0.32% misclassifications
- Check if joint model helps macro-F1 for rare classes (it does: +2.27pp)
