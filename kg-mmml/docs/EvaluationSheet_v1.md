# Evaluation Checklist

## Semantic Retention (SRS)
- [ ] AtP ≥ 0.95: _____ (actual)
- [ ] HP ≥ 0.25: _____ (auto-taxonomy coverage)
- [ ] AP ≥ 0.99: _____ (directional integrity)
- [ ] SRS ≥ 0.75: _____ (weighted)

## Task Performance
- [ ] Baseline micro-F1: _____
- [ ] KG micro-F1: _____
- [ ] Delta ≥ +3pp: _____ (YES/NO)

## Latency (N=10³-10⁴)
- [ ] p50 < 50ms: _____
- [ ] p95 < 150ms: _____
- [ ] p99/p95 ratio < 2.0: _____

## Reproducibility
- [ ] Seeds fixed: [13, 17, 23, 29, 31]
- [ ] Configs pinned: Yes
- [ ] Data snapshot: data/kg/sec_edgar_2025-10-11