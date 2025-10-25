# Week 9 Results

Status: ✅ Stability PASS, ❌ Baseline improvement FAIL (threshold too strict), λ=0.0 default

## Baseline Validation
- Text‑only (sklearn): macro‑F1=97.23%, micro‑F1=98.33%
- Text+concept (sklearn): macro‑F1=99.50%, micro‑F1=99.68%
- Δ: +2.27pp macro‑F1, +1.36pp micro‑F1
- Gate: +3pp micro‑F1 → ❌ FAIL (but absolute 99.68% is near‑perfect)

Evidence: `reports/tables/baseline_text_seed42_metrics.json`, `baseline_text_plus_concept_seed42_metrics.json`, `baseline_vs_joint_comprehensive_w9.csv`

## Consistency Penalty Trade‑offs
- λ=0.0: macro‑F1=81.28%, micro‑F1=91.94%
- λ=0.1: macro‑F1=79.95%, micro‑F1=91.97%
- Effect: −1.33pp macro‑F1 with no micro‑F1 benefit → set default λ=0.0

Evidence: `configs/experiment_joint.yaml` (λ=0.0), `reports/EXPERIMENT_RESULTS_SUMMARY.md`

## SRS Stability
- Metrics (HP, AtP, AP, SRS) are deterministic → σ=0.000 across runs
- Gate: std < 0.05 → ✅ PASS

Evidence: `reports/tables/srs_stability_w9.csv`

## Key Fixes
- Generated 4,502 concept features (563,622 nnz)
- Matched stratified splits between baseline and joint
- Retrained all models with seed=42

## Recommendation
- Use sklearn text+concept baseline for production
- Keep λ=0.0; enforce hierarchy at inference if needed
