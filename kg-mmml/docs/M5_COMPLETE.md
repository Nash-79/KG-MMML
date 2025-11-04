# Milestone M5 Complete: Joint Objective Analysis

**Week 9-10 deliverable**: Minimal joint objective (consistency penalty on directional edges); one ablation; document trade-offs.

## Summary

Tested whether adding a consistency penalty (λ) on directional edges would improve classification performance beyond the text+concept baseline. Result: **No**. The simpler model (λ=0.0, no penalty) outperforms constrained variants across all metrics.

## Experimental Setup

**Hypothesis**: Enforcing hierarchy constraints through a consistency penalty should improve micro-F1 by:
1. Preventing violations of parent-child relations during embedding
2. Forcing the model to respect is-a hierarchy structure
3. Improving generalization on rare classes

**Method**:
- Baseline: Text (TF-IDF) only
- Joint (λ=0.0): Text + concept features, no penalty
- Joint (λ>0): Text + concept features with consistency penalty on directional edges

**Consistency penalty formulation**:
```
L_consistency = λ × mean(max(0, d(child, parent) - d(child, non-parent)))
```
Where d() is cosine distance in embedding space. Penalizes cases where children are closer to non-parents than to their actual parents.

## Results

| Configuration | Micro-F1 | Macro-F1 | Training Time | Stability |
|--------------|----------|----------|---------------|-----------|
| Text only (baseline) | 98.32% | - | Fast | Stable |
| Joint (λ=0.0) | **99.68%** | **81.28%** | Moderate | Stable |
| Joint (λ=0.1) | 99.21% | 80.15% | Slow | Unstable |
| Joint (λ=0.5) | 98.87% | 79.42% | Very slow | Very unstable |

**Key finding**: Adding the penalty makes things worse, not better.

## Trade-off Analysis

### 1. Simplicity vs Sophistication

**λ=0.0 (simple)**: Concept features as binary indicators. Model learns co-occurrence patterns naturally.

**λ>0 (sophisticated)**: Attempts to enforce hierarchy explicitly through loss function.

**Winner**: Simple model. The concept features already capture hierarchy implicitly. Forcing it explicitly adds complexity without benefit.

### 2. Training Cost

**λ=0.0**:
- 20 epochs, batch_size=128
- Converges smoothly
- ~5 minutes on CPU

**λ>0**:
- Requires more epochs to converge (30-40)
- Loss oscillates, especially for rare classes
- ~15-20 minutes
- Hyperparameter tuning needed (λ value, margin, sampling)

**Winner**: λ=0.0. Not worth 3-4× training time for worse results.

### 3. Semantic Preservation

**Question**: Does the penalty help preserve KG structure?

**Answer**: No evidence for it. SRS components remain identical:
- HP = 0.2726 (same)
- AtP = 0.9987 (same)
- AP = 1.0000 (same)

SRS measures the graph structure directly, not the learned embeddings. The penalty affects embeddings but doesn't change the underlying graph quality.

### 4. Performance on Rare Classes

**Hypothesis**: Penalty should help rare classes by enforcing hierarchy.

**Reality**:
- λ=0.0: Macro-F1 = 81.28% (+2.27pp over baseline)
- λ=0.1: Macro-F1 = 80.15% (worse)

Rare classes benefit from concept features, but penalty doesn't add value.

## Why Doesn't the Penalty Help?

**Three explanations**:

1. **Concept features are sufficient**: Binary presence/absence of concepts already encodes hierarchy through co-occurrence. If "AccountsReceivable" appears, "CurrentAssets" likely appears nearby. Model learns this naturally.

2. **Loss function mismatch**: Classification loss (cross-entropy) optimizes for category separation. Consistency loss optimizes for parent-child proximity. These objectives conflict rather than complement.

3. **Data sparsity**: SEC EDGAR filings don't violate hierarchy. The data is already consistent. Penalizing violations of a constraint that's never broken doesn't help.

## Addressing the +3pp Micro-F1 Gate

**Gate requirement**: Demonstrate ≥+3.0pp micro-F1 improvement when adding KG features to text baseline.

**Actual result**: +1.36pp improvement (98.32% → 99.68%).

### Why Did We Miss the Gate?

**Ceiling effect**: Baseline is already at 98.32%. Getting to 101.32% is impossible. We're fighting for the last 1.68% of possible improvement.

**Gate design issue**: The +3pp threshold was set assuming a weaker baseline (e.g., 85-90% accuracy). At 98%, asking for +3pp means achieving near-perfection.

### Alternative Interpretations

**1. Macro-F1 tells a different story**:
- Baseline macro-F1: 79.01%
- Joint macro-F1: 81.28%
- Improvement: +2.27pp

Macro-F1 weights rare classes equally. This shows concept features **do** help where it matters most.

**2. Concept features deliver semantic value beyond micro-F1**:
- Near-perfect accuracy on concept-rich documents (99.68%)
- SRS shows we're preserving graph structure (0.7571 ≥ 0.75)
- Model can explain predictions via concept presence

**3. Production vs research trade-off**:
- Research goal: Show KG adds value → Achieved via SRS, macro-F1, explainability
- Production goal: Hit accuracy target → Already achieved at 99.68%

### Recommendation on the Gate

**Option A**: Adjust gate threshold
- Revised target: +1.5pp micro-F1 at baselines >95%
- Rationale: Ceiling effects make +3pp unrealistic at high accuracy

**Option B**: Accept result with discussion
- Document ceiling effect in Results section
- Point to macro-F1 (+2.27pp) and SRS (0.7571) as evidence of KG value
- Argue: Research contribution is the framework (SRS metric, hybrid architecture), not hitting an arbitrary percentage threshold

**Option C**: Try alternative KG representations
- Attempt: Graph neural network embeddings (GNN)
- Time cost: High (W11-12 would be consumed)
- Risk: May not help given ceiling effect

**My recommendation**: **Option B**. The research has succeeded in its core goals (semantic preservation + operational performance). The +3pp gate was too strict given baseline quality. Document this honestly as a research finding about ceiling effects in high-accuracy regimes.

## Production Recommendation

**Deploy**: Scikit-learn baseline (text + concept features, λ=0.0)

**Reasons**:
1. Simpler: No PyTorch dependency, fewer hyperparameters
2. Faster: Training and inference both faster
3. Better: Outperforms constrained variants
4. Stable: No loss oscillation or convergence issues
5. Production-ready: Deterministic, no random initialization sensitivity

**Do not deploy**: Joint model with consistency penalty (λ>0)
- Adds complexity without benefit
- Training instability
- Slower inference
- Not justified by results

## Decisions for M6 Onwards

1. **Use λ=0.0 model as production baseline**: Text + concept features, no penalty
2. **SRS as quality monitor**: Track HP/AtP/AP in production; expect zero variance
3. **Enforce hierarchy post-hoc if needed**: If predictions violate known constraints, filter them after inference rather than during training
4. **Focus M6 on consolidation**: Gather all metrics, prepare for robustness tests (M7)

## Open Questions for Later Phases

**M7 (Robustness)**:
- How much does performance drop if taxonomy is removed entirely?
- What if unit assignments are noisy (simulating data quality issues)?

**M8 (Scalability)**:
- Can we scale to larger corpora (N ≥ 10⁴) with hybrid architecture?
- Does graph-filtered retrieval maintain latency at scale?

**M9 (Analysis)**:
- What are the 0.32% of cases where the model fails?
- Are there systematic error patterns?

## Conclusion

M5 tested whether explicit semantic constraints improve classification. They don't. Simpler is better. The text+concept baseline (λ=0.0) is the production choice.

The +3pp micro-F1 gate was missed due to ceiling effects. However, the research succeeds in its core goals: semantic preservation (SRS ≥ 0.75), operational performance (p99 < 150ms), and honest evaluation (documenting failures).

**M5 status**: ✅ **COMPLETE**

**Next milestone**: M6 (consolidation, calibration, tidy outputs)
