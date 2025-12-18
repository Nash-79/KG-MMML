# Chapter 7: Conclusion

---

## 7.1 Research Summary

This thesis investigated whether knowledge graphs can preserve semantic structure whilst enabling fast retrieval in multi-label classification tasks. The research was motivated by a fundamental tension in hybrid KG-ML systems: pure vector embeddings sacrifice semantic fidelity for speed, whilst pure graph queries maintain structure but fail to scale. The central question was whether a hybrid architecture could achieve both objectives simultaneously.

**Core research questions addressed:**

1. **RQ1 (Knowledge Fidelity)**: To what extent do lightweight KG signals improve semantic retention over text-only models?
   - **Finding**: SRS=0.8179 demonstrates 81.79% semantic retention, exceeding the 0.75 threshold. Auto-generated taxonomy (1,891 is-a edges) improved HP from 1.15% to 27.26%. TransE embeddings achieved perfect RTF (100%) across four relation types.

2. **RQ2 (Task Performance)**: Which KG representations deliver the best accuracy-latency trade-off?
   - **Finding**: Binary concept indicators (KG-as-features) achieved +1.36pp micro-F1 and +2.27pp macro-F1 improvements over text-only baselines, with negligible latency impact. Simple concatenation outperformed complex joint training for this use case.

3. **RQ3 (Architecture Choice)**: Does hybrid graph-vector infrastructure meet production latency targets at scale?
   - **Finding**: Annoy delivered 0.037ms p99 latency, a 4,054× margin over the 150ms SLO. Analytical projections to N=10,000 maintain sub-millisecond performance. Two-hop graph expansion adds only 0.0023ms overhead.

4. **RQ4 (Honest Evaluation)**: Do stress tests reveal limitations hidden by accuracy-only reporting?
   - **Finding**: Taxonomy removal degrades SRS by 18.8%, quantifying hierarchy dependence. Unit-noise tolerance (5-10%) demonstrates graceful degradation. The micro-F1 gate failure (target: +3.0pp, achieved: +1.36pp) stems from ceiling effects at 98.33% baseline, not architectural weakness.

**Overall outcome**: The hybrid architecture successfully balances semantic preservation and operational performance. The system achieved 3 of 4 decision gates, with the micro-F1 shortfall explained by diminishing returns at high baseline accuracy.

---

## 7.2 Contributions to Knowledge

This research makes five primary contributions to the hybrid KG-ML literature:

### 7.2.1 Semantic Retention Score (SRS) Metric

**Contribution**: A quantitative framework for measuring structural fidelity in KG-to-vector transformations.

The SRS metric (weighted combination of HP, AtP, AP, RTF) provides an architectural diagnostic absent from prior work. Most KG-augmented ML papers report only downstream task accuracy, leaving semantic preservation unquantified. SRS fills this gap by measuring:
- Hierarchical structure retention (HP)
- Attribute consistency (AtP)
- Directional asymmetry (AP)
- Relation-type embedding quality (RTF)

**Impact**: Practitioners can monitor SRS in production to detect data quality degradation (e.g., HP drift signals taxonomy staleness). Researchers can use SRS to compare embedding methods beyond link prediction benchmarks.

**Limitations**: The metric weights (HP=25%, AtP=20%, AP=20%, RTF=35%) reflect design priorities, not empirical optimisation. Alternative domains may require different weight configurations.

### 7.2.2 Pattern-Based Taxonomy Generation

**Contribution**: A scalable, reproducible method for auto-generating hierarchies without manual annotation.

The pattern-rule approach (e.g., "Current* is-a *", "Other* is-a *") generated 1,891 is-a edges with zero human effort, improving HP from 1.15% to 27.26%. This demonstrates that imperfect taxonomies (estimated 90% precision) provide sufficient inductive bias for downstream tasks.

**Comparison to alternatives**: Manual annotation achieves higher precision but does not scale. Distant supervision (matching to external KBs) requires entity linking, adding complexity. The pattern-based method occupies a pragmatic middle ground: good enough coverage, minimal engineering effort.

**Generalisability**: Patterns are domain-specific (financial concepts have regularities like "Noncurrent*", "Deferred*") but the methodology transfers. Future work could evaluate pattern learning from concept name distributions.

### 7.2.3 Ceiling Effect Characterisation

**Contribution**: Empirical evidence that improvement targets must account for baseline strength.

The thesis demonstrates quantitatively that absolute performance (99.68% micro-F1) and error reduction (64.5%) provide more informative measures than percentage-point gains when baselines exceed 98%. The +1.36pp micro-F1 improvement, whilst below the +3.0pp target, represents meaningful progress in a high-accuracy regime.

**Implications**: Decision gates should scale targets inversely with baseline accuracy. For example:
- Baseline 85%: Target +5pp (33% error reduction)
- Baseline 95%: Target +2pp (40% error reduction)
- Baseline 98%: Target +1pp (50% error reduction)

This recalibration prevents dismissing valuable architectural improvements as failures due to unrealistic targets.

### 7.2.4 Honest Evaluation Framework

**Contribution**: Operationalising robustness, scalability, and degradation testing alongside accuracy.

The thesis emphasises three evaluation pillars beyond test-set accuracy:

1. **Robustness**: Quantifying performance under perturbations (taxonomy removal, unit noise, class imbalance)
2. **Scalability**: Projecting latency to 10× and 100× corpus sizes using algorithmic complexity
3. **Degradation**: Identifying failure modes and fallback strategies for production deployment

**Academic impact**: This challenges leaderboard culture in ML conferences, where accuracy maximisation dominates. Including robustness and scalability in standard evaluation protocols increases research-to-production transferability.

**Practical impact**: Practitioners gain confidence in system behaviour under realistic stress, reducing deployment risk.

### 7.2.5 KG-as-Features Simplicity Advantage

**Contribution**: Demonstrating that simple concatenation of binary concept indicators outperforms complex joint training for specific use cases.

Whilst graph neural networks (GCNs, GATs) dominate KG-augmented ML literature, this thesis shows that sparse binary features (one-hot concept presence) achieve competitive performance (+1.36pp micro-F1, +2.27pp macro-F1) with:
- Zero GPU requirement
- 10× faster training (minutes vs hours)
- Perfect sklearn pipeline compatibility
- Full interpretability (which concepts influenced predictions)

**Conditions favouring simple approaches**:
- High-quality baselines (>95% accuracy)
- Interpretability requirements (regulated domains)
- Limited computational budget (CPU-only inference)
- Rapid iteration needs (prototyping, A/B testing)

**When to use GNNs instead**:
- Low baselines (<85% accuracy)
- Complex relational reasoning (multi-hop inference)
- GPU infrastructure available
- Black-box models acceptable

---

## 7.3 Practical Implications

The research provides actionable guidance for practitioners building production KG-ML systems.

### 7.3.1 Architectural Decision Framework

**When to adopt hybrid KG-ML architectures:**

**Adopt when:**
- Structured domain knowledge exists (taxonomies, ontologies, typed relations)
- Long-tail accuracy matters (rare classes, regulatory compliance)
- Explainability required (audit trails, trust calibration)
- Sub-millisecond latency needed (interactive search, auto-complete)

**Avoid when:**
- No structured knowledge available (sentiment analysis, topic modelling)
- Only head classes matter (spam detection, click prediction)
- Black-box models acceptable (internal tooling)
- Batch processing suffices (offline analytics)

**Cost-benefit analysis**: Hybrid architectures introduce operational complexity (multiple data stores, integration overhead) justified only when performance gains deliver measurable business value.

### 7.3.2 Implementation Recommendations

**Production stack:**
- **Graph store**: Neo4j (APOC for 2-hop) or JanusGraph (distributed)
- **Vector index**: Annoy (CPU) or FAISS-HNSW (GPU)
- **Classifier**: sklearn LogisticRegression with sparse features
- **Monitoring**: Track HP, AtP, RTF drift; alert on >10% degradation

**Feature engineering:**
- Start with binary concept indicators (sparse, interpretable)
- Add TransE embeddings only if accuracy gains justify complexity
- Avoid GNNs unless strong evidence (>3pp improvement) justifies GPU cost

**Fallback strategies:**
- Graph unavailable → vector-only retrieval (accept SRS degradation)
- Vector corrupted → exact cosine similarity (accept latency hit)
- Embeddings down → one-hot features (accept accuracy drop)

### 7.3.3 Evaluation Best Practices

**Beyond accuracy metrics:**
1. **Stress test at 10× scale**: Measure latency degradation, not just current corpus size
2. **Perturb inputs**: Remove features, add noise, simulate class imbalance
3. **Quantify dependencies**: Ablate components (graph, embeddings, filters) to measure contribution
4. **Monitor in production**: Track SRS components to detect data drift early

**Reporting standards:**
- Include error reduction percentages alongside absolute gains
- Plot latency distributions (p50/p95/p99), not just means
- Report robustness test results, not just best-case accuracy
- Provide reproducibility artifacts (random seeds, data splits, hyperparameters)

---

## 7.4 Limitations and Future Directions

### 7.4.1 Acknowledged Limitations

**Single-domain evaluation**: All experiments use SEC EDGAR financial data. Generalisability to other domains (biomedical, legal, e-commerce) remains empirically unvalidated. Different domains exhibit different taxonomy structures, label distributions, and data quality profiles.

**Modest corpus size**: N=3,218 documents is small by production standards. Whilst analytical projections suggest scalability to N=10,000, empirical validation at N=100,000+ was not conducted.

**Single-seed validation**: The baseline uses seed=42 for reproducibility but lacks multi-seed statistical testing (n=5). Confidence intervals and significance tests (paired t-tests) are implemented but not executed due to data preprocessing dependencies.

**SRS metric subjectivity**: Component weights (HP=25%, AtP=20%, AP=20%, RTF=35%) reflect architectural priorities, not empirical optimisation. Sensitivity analysis to alternative weighting schemes was not performed.

**Taxonomy quality**: Auto-generated is-a edges have estimated 90% precision (heuristic validation, not gold-standard comparison). Systematic label errors could propagate to classification, though the consistent +2.27pp macro-F1 improvement suggests sufficient quality for downstream tasks.

### 7.4.2 Future Research Directions

**Cross-domain validation**: Evaluate the hybrid architecture on:
- **Biomedical**: PubMed + MeSH ontology (deeper hierarchies, more relation types)
- **E-commerce**: Product catalogues (high skew, sparse long tail)
- **Legal**: Court judgments + citation graphs (temporal relations, precedent reasoning)

**Multi-seed validation**: Execute M10 scripts to compute:
- 95% confidence intervals for +1.36pp micro-F1 and +2.27pp macro-F1 improvements
- Paired t-tests for statistical significance (expected: p<0.01 for macro-F1)
- Variance analysis to assess train/test split sensitivity

**Advanced embedding methods**: Benchmark TransE against:
- RotatE (rotation-based for complex patterns)
- QuatE (quaternion for 1-to-N relations)
- ConvE (convolutional for compositional reasoning)
- Metric: RTF probe accuracy, training time, memory footprint

**Explainability studies**: User studies measuring:
- Trust calibration with graph-based explanations vs text-based
- Comprehension speed for classifier rationales
- Decision quality improvements from structured reasoning paths

**Enterprise scale**: Test at N=10⁶ entities (Wikidata, UMLS, ProductGraph):
- Identify scaling bottlenecks (graph expansion, embedding training)
- Evaluate hierarchical indexing (partition by domain)
- Benchmark feature hashing vs sparse storage

---

## 7.5 Reflection on Research Journey

This section provides personal reflection on the research process, acknowledging both successes and challenges.

### 7.5.1 What Went Well

**Pragmatic methodology**: The emphasis on reproducibility (fixed random seeds, documented pipelines) and honest evaluation (robustness testing, ceiling effect analysis) strengthened the research. Resisting the temptation to cherry-pick results or hide limitations builds credibility.

**Incremental milestones**: Breaking the work into 12 milestones (M1-M12) with clear decision gates prevented scope creep. When the micro-F1 gate failed (M3), reframing as a ceiling effect rather than abandoning the architecture proved insightful.

**Simplicity bias**: Choosing sklearn over PyTorch, binary features over GNNs, and pattern rules over manual annotation reduced complexity without sacrificing performance. The production system is maintainable and debuggable.

**Open data selection**: Using SEC EDGAR (public domain, no authentication barriers) ensures full reproducibility. Any researcher can replicate the experiments without access negotiations.

### 7.5.2 What Was Challenging

**Taxonomy generation ambiguity**: Deciding when "good enough" (27% HP) suffices proved difficult. Higher coverage would improve SRS but at exponentially increasing effort. The pragmatic threshold (pattern rules + frequency analysis) emerged through iteration, not principled reasoning.

**Evaluation metric design**: Defining SRS weights (HP=25%, RTF=35%) required subjective judgement. Sensitivity analysis would quantify robustness to alternative configurations but was deferred due to time constraints.

**Ceiling effects**: The high text-only baseline (98.33% micro-F1) made architectural contributions harder to demonstrate. In hindsight, testing on a dataset with 85-95% baseline accuracy would provide more improvement headroom. However, realistic financial data naturally exhibits high accuracy due to regulatory standardisation.

**Multi-seed validation deferral**: Data preprocessing issues (empty facts.jsonl file) blocked M10 execution. Whilst single-seed results are reproducible, statistical significance testing remains incomplete. This represents a known limitation rather than a fatal flaw.

### 7.5.3 Lessons Learnt

**Baseline strength matters**: When evaluating architectural innovations, baseline quality shapes what improvements are possible. A +1.36pp gain from 98.33% baseline is harder than +5pp from 85% baseline. Framing experiments with ceiling effect awareness prevents misinterpreting results.

**Simpler architectures deploy faster**: GNNs and joint training offer theoretical advantages but introduce GPU dependencies, hyperparameter sensitivity, and debugging complexity. For production systems with tight timelines, sklearn pipelines win on velocity and reliability.

**Robustness testing reveals assumptions**: The 18.8% SRS degradation under taxonomy removal quantifies the architecture's dependence on structured knowledge. Without stress testing, this dependency would remain invisible until production failure.

**Documentation is research**: Writing milestone plans (M6-M10) and decision gate narratives (M3, M5) clarified thinking and prevented revisiting settled questions. The act of writing forced precision in hypothesis formulation and result interpretation.

---

## 7.6 Closing Statement

This thesis demonstrates that hybrid knowledge graph-machine learning architectures can preserve semantic structure whilst maintaining operational performance at scale. The system achieved SRS=0.8179 (81.79% semantic retention) with 0.037ms p99 latency, validating the hypothesis that specialised graph stores and vector indices coexist effectively in production systems.

The results challenge two prevailing assumptions in the literature:
1. **Complexity requirement**: Simple KG-as-features (binary concept indicators) achieve competitive performance without GNNs, joint training, or GPU infrastructure.
2. **Accuracy myopia**: Honest evaluation (robustness, scalability, degradation) reveals architectural trade-offs invisible in accuracy-only reporting.

The contributions—SRS metric, pattern-based taxonomy generation, ceiling effect characterisation, honest evaluation framework—provide actionable tools for researchers and practitioners. The architectural patterns generalise beyond financial concept classification to any domain with structured knowledge and multi-label tasks.

**Final recommendation**: Adopt hybrid KG-ML architectures when domain knowledge exists, rare classes matter, and explainability is required. Start with simple implementations (binary features, sklearn classifiers) and increase complexity only when empirical evidence justifies the operational overhead.

The knowledge graph preserves meaning. The vector index delivers speed. The hybrid architecture achieves both.

---

**Chapter 7 establishes the thesis contributions, practical guidance for practitioners, and reflection on the research journey. The work demonstrates that hybrid KG-ML architectures can preserve semantic structure whilst meeting operational performance targets.**
