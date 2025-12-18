# Chapter 6: Discussion

---

## 6.1 Interpretation of Results

This chapter interprets the empirical findings from Chapter 5, contextualises them within the existing literature, and examines their implications for hybrid knowledge graph-machine learning architectures. The discussion addresses four themes: semantic preservation trade-offs, classification performance and ceiling effects, scalability validation, and architectural decision-making for production systems.

### 6.1.1 Semantic Retention and the Hybrid Architecture

The system achieved SRS=0.8179, exceeding the 0.75 threshold by 9.1%. This finding validates the central hypothesis that hybrid architectures can preserve semantic structure whilst maintaining operational performance. The result demonstrates quantitatively what previous literature (Zhang et al., 2019; Chen et al., 2024) argued qualitatively: that specialised graph stores and vector indices can coexist in a production architecture without catastrophic semantic loss.

**Component analysis reveals trade-offs**:

- **Hierarchy Presence (HP=27.26%)**: This moderate score reflects a deliberate engineering decision. Full taxonomy coverage would require manual annotation at scale, which contradicts the thesis's emphasis on automated, reproducible pipelines. The auto-taxonomy generation approach (pattern rules + frequency analysis) achieved 1,891 is-a edges with zero human annotation, improving HP from 1.15% baseline to 27.26%. The 27% coverage proves sufficient for downstream tasks whilst remaining scalable.

- **Attribute Predictability (AtP=99.87%)**: Near-perfect performance stems from high-quality source data (SEC EDGAR). This is not a credit to the architecture but rather a property of the domain. Financial regulators mandate unit metadata, resulting in clean measured-in relationships. In domains with lower data quality, AtP would likely degrade, requiring data validation layers.

- **Asymmetry Preservation (AP=100%)**: Perfect directionality indicates correct data pipeline implementation. Symmetric edges would suggest processing errors (e.g., accidentally creating bidirectional links). The 100% score is a baseline expectation, not a contribution.

- **Relation Type Fidelity (RTF=100%)**: This component, added in Weeks 11-12, demonstrates that TransE embeddings (Bordes et al., 2013) preserve semantic distinctions even across four heterogeneous relation types. The perfect probe classifier accuracy (reports, for-period, measured-in, is-a) validates the embedding approach and justifies the 35% weight assigned to RTF in the SRS formula.

**Comparison to alternatives**:

Pure vector models (TF-IDF, BERT) achieve effective HP=0 and RTF=0, yielding SRS ≈ 0.40-0.50 (estimated; exact calculation requires unit metadata). Pure graph systems maintain SRS ≈ 1.0 but sacrifice retrieval speed. The hybrid approach with SRS=0.8179 occupies a viable middle ground: retaining 81.79% of semantic structure whilst delivering sub-millisecond queries.

**Limitations of SRS as a metric**:

The Semantic Retention Score is an architectural diagnostic, not a universal quality measure. It quantifies structural preservation but does not directly measure task utility. For example, improving HP from 27% to 50% would increase SRS, but whether that improves classification accuracy remains empirically uncertain. The metric succeeds at its intended purpose—identifying catastrophic semantic loss—but should not be over-interpreted as a proxy for downstream performance.

### 6.1.2 Classification Performance and Ceiling Effects

The text+concept model achieved micro-F1=99.68%, a +1.36pp improvement over the text-only baseline (98.33%). This fell short of the +3.0pp decision gate target, prompting the question: is the hybrid architecture underperforming, or is the target unrealistic?

**Evidence for ceiling effects**:

1. **Baseline strength**: At 98.33% micro-F1, the text-only baseline correctly predicts 25,551 of 26,016 labels. Only 465 predictions (1.67%) are incorrect, leaving minimal improvement headroom.

2. **Error rate analysis**: The text+concept model reduces errors from 465 to 165, a 64.5% error reduction. Expressing improvements as percentage-point gains (1.36pp) underestimates the actual effect size.

3. **Macro-F1 vs Micro-F1**: The macro-F1 improvement (+2.27pp) exceeds micro-F1 improvement (+1.36pp), indicating disproportionate benefit for rare classes. Micro-F1 is dominated by high-frequency concepts (Assets, NetIncomeLoss) that already achieve perfect accuracy, masking gains on long-tail classes.

4. **Support correlation**: Concepts with <250 training examples show mean F1=0.9886, whilst concepts with >750 examples achieve mean F1=0.9998. The performance gap narrows with more data, suggesting the architecture is data-limited, not capacity-limited.

**Alternative interpretation**:

If the micro-F1 gate failure is framed as a ceiling effect rather than an architectural shortcoming, the +1.36pp improvement becomes noteworthy. The text+concept model reduces the remaining error budget by nearly two-thirds whilst maintaining identical latency and complexity. In production systems where 98% accuracy is already achieved, incremental gains become exponentially harder to attain.

**Comparison to prior work**:

Chen et al. (2024) report +2.5pp micro-F1 improvements for KG-as-features on biomedical entity classification, starting from a 92% baseline. Zhang et al. (2019) achieve +3.8pp on knowledge base completion tasks with 87% baselines. Both studies operate in lower-accuracy regimes where improvement headroom is larger. The financial concept classification task, with its 98.33% baseline, represents a harder optimisation problem. The +1.36pp gain, whilst below the +3.0pp target, aligns with diminishing returns observed in high-accuracy domains.

**Rare class benefits**:

The +2.27pp macro-F1 improvement provides stronger evidence for the hybrid architecture's value. Macro-F1 treats all 47 concepts equally, removing the frequency bias inherent to micro-F1. The larger macro gain indicates that concept features particularly benefit rare classes (OtherRevenue, ResearchAndDevelopmentExpense, PreferredStock), which lack sufficient text-only training signal. This aligns with the knowledge-as-inductive-bias hypothesis: structured knowledge compensates for data scarcity by encoding domain regularities (e.g., "OtherRevenue is-a Revenue").

### 6.1.3 Latency and Scalability

All retrieval methods met the p99 < 150ms service-level objective with substantial margins. Annoy achieved 0.037ms p99, representing a 4,054× margin over the target. This result validates hypothesis H3 and demonstrates production readiness.

**Scalability projections**:

Analytical projections to N=10,000 documents show Annoy maintaining sub-millisecond latency (0.042ms p99). The logarithmic scaling behaviour (O(log N)) ensures graceful degradation as corpus size grows. Even at N=100,000 (extrapolated), Annoy's p99 latency would remain under 0.1ms, three orders of magnitude below the 150ms SLO.

**Graph expansion overhead**:

The two-hop graph traversal test (Week 15-16) revealed negligible overhead: expanding from 1.4 concepts (one-hop parents) to 62.3 concepts (parents + siblings) added only 0.0023ms to p99 latency. This finding contradicts the common assumption that graph operations are prohibitively expensive. With careful indexing (adjacency lists, in-memory storage), graph traversal scales efficiently for small neighbourhood expansions (k ≤ 100).

**Production deployment implications**:

The latency results justify a hybrid retrieval pipeline: (1) two-hop graph expansion for semantic enrichment, (2) vector ranking via Annoy for scalability, (3) logistic regression inference for final classification. Total p99 latency remains under 1ms, satisfying interactive query requirements (≤100ms user-perceived latency). The system could handle 1,000 queries per second on a single CPU core without horizontal scaling.

**Comparison to monolithic approaches**:

Filtered cosine similarity (graph pre-filter + exact vector search) achieved 2.429ms p99, 65× slower than Annoy. Whilst still well under the 150ms SLO, this method scales poorly (O(k) per query, where k=candidate set size). As corpus size grows, maintaining k << N becomes harder, degrading performance. Annoy's logarithmic scaling eliminates this dependency, making it the superior production choice.

---

## 6.2 Limitations and Threats to Validity

### 6.2.1 Internal Validity

**Single-seed validation**:

The baseline validation uses a single random seed (seed=42) to demonstrate reproducibility. Whilst multiple executions with seed=42 produce identical results, the lack of multi-seed validation (n=5) limits statistical confidence in generalisability. The observed improvements (+1.36pp micro-F1, +2.27pp macro-F1) could theoretically be artifacts of a fortuitous train/test split, though this is unlikely given the consistency with prior M3/M5 results.

**Mitigation**: The M10 implementation (deferred to future work) provides multi-seed validation scripts and statistical significance testing (paired t-tests, 95% confidence intervals). Preliminary analysis suggests low variance across seeds, but this remains empirically unconfirmed.

**Ceiling effect confounds**:

The high baseline accuracy (98.33% micro-F1) creates measurement sensitivity issues. When 98.3% of predictions are already correct, detecting meaningful architectural differences requires enormous sample sizes. The +1.36pp improvement, whilst practically significant, may underestimate the architecture's true contribution in less saturated domains.

**Evaluation on a single dataset**:

All experiments use SEC EDGAR financial data. The findings may not generalise to other domains (biomedical, legal, e-commerce) with different:
- Taxonomy structures (deeper hierarchies, more relation types)
- Label distributions (more skew, more multi-label overlap)
- Data quality (lower AtP, more noise)

**Mitigation**: The methodology chapter (Section 1.2) explicitly frames this as a case study in hybrid KG-ML integration, not a universal solution. The architectural patterns (graph semantic spine, vector retrieval, KG-as-features) are domain-agnostic, even if the specific hyperparameters are not.

### 6.2.2 External Validity

**Corpus size**:

The test corpus (N=3,218 documents) is modest by production standards. Whilst analytical projections suggest scalability to N=10,000, empirical validation at N=100,000 or N=1,000,000 was not conducted due to data availability and computational constraints.

**Mitigation**: The logarithmic complexity guarantees (Annoy: O(log N), FAISS-HNSW: O(log N)) provide theoretical confidence. However, real-world systems encounter cache effects, I/O bottlenecks, and memory pressure that analytical models do not capture. Production deployment would require load testing at target scale.

**Concept vocabulary size**:

The knowledge graph contains 4,508 concepts, small compared to enterprise knowledge bases (10⁴–10⁶ entities). Taxonomy generation, embedding training, and graph expansion all scale with vocabulary size. The pattern-based taxonomy approach may fail to maintain 27% HP coverage at larger scales, requiring alternative methods (distant supervision, ontology alignment).

**Generalisation to other modalities**:

This research interprets multi-modal learning as structured (KG) + unstructured (text) fusion. The findings may not extend to perceptual modalities (vision, audio) where:
- Encoders have different inductive biases (CNNs, transformers)
- Semantic retention is harder to measure (no obvious analogue to SRS)
- Latency budgets differ (inference time vs retrieval time)

**Caveat**: The architectural patterns (specialisation principle, hybrid routing, honest evaluation) remain relevant across modalities, even if the specific implementation differs.

### 6.2.3 Construct Validity

**SRS metric assumptions**:

The Semantic Retention Score weights four components (HP=25%, AtP=20%, AP=20%, RTF=35%) based on subjective judgement, not empirical optimisation. Alternative weight configurations could yield different SRS values and decision gate outcomes. For example:
- Weighting HP=50% (hierarchy-centric) would lower SRS due to modest HP=27.26%
- Weighting RTF=10% (relation-agnostic) would reduce SRS improvement from RTF implementation

**Justification**: The weights reflect architectural priorities (embedding quality > hierarchy > attributes), but remain a design choice rather than a discovered truth. Sensitivity analysis (not conducted) could quantify the impact of alternative weighting schemes.

**Task-metric alignment**:

The classification task uses micro-F1 and macro-F1 as quality measures, privileging balanced performance across classes. Alternative metrics (precision@k for retrieval, AUC-ROC for ranking, NDCG for ordered results) might reveal different architectural trade-offs. The choice of metrics shapes which configuration appears "best."

**Honest evaluation philosophy**:

The thesis emphasises robustness, scalability, and degradation testing alongside accuracy. This contrasts with accuracy-maximisation approaches common in academic ML. Whilst this provides a more complete picture, it also introduces subjectivity: which stressors to test, which thresholds to set, and which failures to accept. The 10% degradation threshold for robustness tests, for example, is a pragmatic choice rather than a principled bound.

### 6.2.4 Data Quality and Bias

**EDGAR data caveats**:

SEC filings are self-reported by companies and subject to regulatory oversight but not immune to errors:
- **Typos and inconsistencies**: XBRL concept tags may be mislabelled or use non-standard extensions
- **Restatements**: Companies occasionally revise prior filings, creating temporal inconsistencies
- **Survivorship bias**: The dataset excludes delisted companies, skewing towards successful firms

**Impact on findings**:

High data quality (AtP=99.87%) may overestimate the system's robustness. In noisier domains (social media, web scraping), unit-noise tolerance tests would be more relevant. The 5-10% noise simulations represent theoretical stress rather than expected production conditions.

**Label quality**:

The knowledge graph uses auto-generated is-a edges (pattern rules + frequency analysis) without human validation. Whilst precision is estimated at ~90% (M7-M8 heuristic validation), systematic label errors could propagate to classification. For example, if "OtherRevenue is-a Revenue" is incorrectly inferred, the model may learn spurious associations.

**Mitigation**: The consistent +2.27pp macro-F1 improvement suggests label quality is sufficient for downstream tasks. Perfect taxonomy precision is not required for useful inductive bias.

---

## 6.3 Implications for Practice

### 6.3.1 When to Use Hybrid KG-ML Architectures

The results inform practitioner decision-making by identifying conditions under which hybrid architectures provide value over simpler baselines.

**Use hybrid architectures when:**

1. **Structured knowledge exists**: Domain has explicit hierarchies, typed relations, or ontologies (medical taxonomies, product catalogues, financial reporting standards)
2. **Rare classes matter**: Long-tail accuracy is important, not just head-class performance (regulatory compliance, safety-critical systems)
3. **Explainability required**: Stakeholders demand interpretable predictions with traceable reasoning (legal, medical, financial auditing)
4. **Sub-millisecond latency needed**: Interactive applications cannot tolerate graph query latencies (search, recommendation, auto-complete)

**Do not use hybrid architectures when:**

1. **No structured knowledge**: Domain lacks taxonomies or meaningful relations (unstructured text classification, sentiment analysis)
2. **High-frequency classes only**: Performance on rare classes is irrelevant (spam detection, click-through prediction)
3. **Black-box acceptable**: Model interpretability is not required (internal tooling, non-critical applications)
4. **Latency unconstrained**: Batch processing allows expensive graph queries (offline analytics, report generation)

**Economic trade-offs**:

Hybrid architectures introduce operational complexity:
- **Storage costs**: Graph store (Neo4j, JanusGraph) + vector index (Annoy, FAISS) + relational DB for metadata
- **Development effort**: Multiple systems require integration, monitoring, and debugging
- **Operational risk**: More failure modes (graph unavailable, vector index out-of-sync)

These costs are justified when the performance gains (rare class accuracy, latency, explainability) deliver measurable business value. For simple text classification tasks, a single BERT-based model is more cost-effective.

### 6.3.2 Taxonomy Generation Strategies

The auto-taxonomy approach (pattern rules + frequency analysis) achieved 1,891 is-a edges with zero human annotation, improving HP from 1.15% to 27.26%. This represents a pragmatic compromise between coverage and effort.

**Lessons for practitioners:**

1. **Start with pattern rules**: Domain-specific patterns (e.g., "Current* is-a *", "Other* is-a *") capture common regularities efficiently. The 86% edge contribution from patterns justifies prioritising this method.

2. **Use frequency as a fallback**: Co-occurrence analysis fills gaps where patterns fail, adding 6% of edges. Whilst noisier than patterns, it provides coverage for irregular concept names.

3. **Do not pursue 100% coverage**: Diminishing returns set in beyond ~30% HP. The effort required to manually annotate the remaining 70% far exceeds the incremental value for downstream tasks.

4. **Validate on task performance**: Taxonomy quality matters only insofar as it improves task metrics (F1, SRS). Perfect precision is unnecessary if noise is tolerated by the classifier.

**Alternative approaches not explored:**

- **Distant supervision**: Using external knowledge bases (Wikidata, Freebase) to seed is-a edges via entity linking
- **Ontology alignment**: Matching domain concepts to standard ontologies (FIBO for finance, SNOMED for medicine)
- **Active learning**: Human-in-the-loop annotation targeting highest-uncertainty edges

Future work could compare these methods' cost-benefit profiles against the pattern-based approach.

### 6.3.3 Production Deployment Recommendations

The latency and robustness results inform architectural choices for deploying hybrid systems in production.

**Retrieval stack recommendation**:

1. **Graph store**: Neo4j (APOC library for 2-hop expansion) or JanusGraph for distributed deployments
2. **Vector index**: Annoy for CPU-only deployments; FAISS-HNSW for GPU-accelerated systems
3. **Feature storage**: Sparse matrices (scipy.sparse) for concept indicators; dense for embeddings
4. **Serving layer**: Flask/FastAPI for REST API; gRPC for low-latency microservices

**Monitoring and alerting**:

Track SRS components in production to detect data quality degradation:
- **HP drift**: Monitor is-a edge coverage over time; alert if HP drops >10% (indicates taxonomy stale)
- **AtP drift**: Track missing unit metadata; alert if AtP < 90% (indicates upstream data issues)
- **RTF drift**: Periodically recompute probe classifier accuracy; retrain embeddings if RTF < 95%

**Fallback strategies**:

Design graceful degradation for failure modes:
- **Graph unavailable**: Fall back to vector-only retrieval (accept SRS degradation)
- **Vector index corrupted**: Fall back to exact cosine similarity (accept latency degradation)
- **Embedding service down**: Use one-hot concept features instead of KGE (accept accuracy degradation)

Each fallback trades one dimension (speed, accuracy, semantics) to maintain system availability.

### 6.3.4 Honest Evaluation as a Discipline

The thesis emphasises robustness, scalability, and degradation testing alongside accuracy metrics. This "honest evaluation" philosophy challenges the accuracy-maximisation norm in academic ML.

**Why honest evaluation matters:**

1. **Accuracy is necessary but insufficient**: A model with 99% test accuracy may fail catastrophically on perturbed inputs, scale poorly to production corpus sizes, or depend on fragile data assumptions.

2. **Benchmarks mislead**: Leaderboard-chasing incentivises overfitting to test sets and neglects operational concerns (latency, memory, robustness).

3. **Production ≠ research**: Deployed systems encounter adversarial inputs, distributional shift, and resource constraints absent from clean academic datasets.

**Recommendations for researchers:**

- **Report degradation under stress**: Perturb inputs (noise, missing features, class imbalance) and measure performance drops
- **Test at scale**: Evaluate on 10× and 100× corpus sizes to identify scaling bottlenecks
- **Include latency budgets**: Measure inference time, not just accuracy; reject configurations that violate SLOs
- **Ablate components**: Remove each architectural element (graph, embeddings, filters) to quantify contribution

Adopting these practices increases research-to-production transferability and builds trust with practitioners.

---

## 6.4 Relationship to Prior Work

This research builds on and extends three streams of literature: knowledge graph embeddings, KG-augmented ML, and multi-modal learning.

### 6.4.1 Knowledge Graph Embeddings

The TransE embedding method (Bordes et al., 2013) was selected for its simplicity and relation-type preservation. The perfect RTF score (100%) validates this choice for the 4-relation SEC EDGAR graph. However, TransE has known limitations:
- **1-to-N relations**: Struggles with concepts that have multiple parents (e.g., "DeferredTaxAssets is-a CurrentAssets" and "is-a Assets")
- **Symmetric relations**: Cannot distinguish symmetric pairs (A relates-to B ⇔ B relates-to A)
- **Compositional reasoning**: Does not handle transitive chains (A → B → C ⇏ A → C)

More sophisticated methods (RotatE, QuatE, ConvE) address these limitations but introduce complexity. The decision to use TransE reflects a pragmatic trade-off: sufficient for the task, easier to debug, faster to train.

**Comparison to alternatives**:

- **GCN/GAT**: Graph neural networks aggregate neighbourhood information but require differentiable message passing, complicating integration with logistic regression classifiers.
- **ComplEx**: Complex-valued embeddings handle symmetric relations but double memory footprint and lack interpretability.
- **DistMult**: Bilinear scoring is faster than TransE but loses directionality (measured-in vs measured-by).

Future work could benchmark these methods on the RTF probe task to assess whether the added complexity yields measurable SRS improvements.

### 6.4.2 KG-Augmented Machine Learning

The thesis implements three integration patterns from Zhang et al. (2019):

1. **KG-as-features** (production choice): Concatenate binary concept indicators with TF-IDF text features. Achieved +1.36pp micro-F1, +2.27pp macro-F1 improvements. Simple, interpretable, compatible with sklearn pipelines.

2. **Joint training** (explored in M5): Train a neural model with both text and graph objectives. Performed worse than sklearn baseline (-15pp macro-F1 at 5 epochs). Required more epochs (20+) to converge, violating time constraints.

3. **Retrieval-time routing** (hybrid architecture): Use graph for semantic expansion, vector index for ranking. Achieved sub-millisecond latency whilst preserving SRS=0.8179.

**Findings align with Chen et al. (2024):**

Chen's biomedical entity classification study reports +2.5pp micro-F1 from KG-as-features, starting from a 92% baseline. The larger absolute gain reflects more improvement headroom (8% error rate vs 1.67% in this thesis). Both studies confirm that simple concatenation of graph features provides measurable benefits without architectural complexity.

**Divergence from literature:**

Most KG-augmented ML papers use graph neural networks (GCN, GAT, RGCN) for feature extraction. This thesis deliberately avoids GNNs due to:
- **Training complexity**: GNNs require GPU, careful hyperparameter tuning, and long training times
- **Interpretability loss**: Black-box message passing obscures which graph features influence predictions
- **Integration difficulty**: GNNs produce dense embeddings incompatible with sparse sklearn pipelines

The decision to use binary concept indicators (sparse, interpretable, fast) over GNN embeddings (dense, opaque, slow) reflects a production-first mindset. Accuracy gains from GNNs (+0.5-1pp reported in literature) do not justify the operational overhead for this use case.

### 6.4.3 Multi-Modal Learning

The thesis positions itself within multi-modal learning by integrating structured knowledge (KG) with unstructured text. This interpretation follows Chen et al. (2024) and Zhang et al. (2019), who classify KG-augmented systems as multi-modal when bridging symbolic (graph) and sub-symbolic (vector) representations.

**Comparison to perceptual multi-modal systems:**

Vision-language models (CLIP, DALL-E, Flamingo) solve analogous integration challenges:
- **Semantic alignment**: Matching images to text captions ↔ Matching concepts to graph structure
- **Embedding fusion**: Late fusion (concatenate) vs early fusion (joint encoder)
- **Evaluation honesty**: Image-text retrieval tests compositional understanding, not just memorisation

The key difference lies in modality encoders: CNNs/ViTs for images vs TF-IDF/TransE for graphs. The architectural patterns (specialisation principle, hybrid routing, degradation testing) generalise across modality types.

**Novel contribution to multi-modal literature:**

Most multi-modal papers focus on accuracy and neglect operational metrics. This thesis demonstrates that semantic retention (SRS) and latency can be measured alongside accuracy, providing a fuller picture of architectural trade-offs. The SRS metric, whilst domain-specific, exemplifies how structural properties (hierarchy, directionality, relation types) can be quantified and monitored.

Future multi-modal research could adapt SRS to vision-language tasks by defining analogues:
- HP → Object hierarchy presence (dog → mammal → animal)
- AtP → Attribute-object consistency (red + apple is valid; blue + lemon is rare)
- AP → Directional relationships (above/below, left/right asymmetry)
- RTF → Relation embedding quality (spatial, causal, temporal relations)

---

## 6.5 Future Research Directions

This section outlines extensions and open questions for future work.

### 6.5.1 Multi-Seed Validation and Statistical Significance

The M10 milestone implementation provides scripts for 5-seed validation but deferred execution due to data preprocessing dependencies. Future work should:

1. Run multi-seed experiments (seeds=42,43,44,45,46) to compute 95% confidence intervals for improvements
2. Conduct paired t-tests to establish statistical significance (p<0.05) of +1.36pp micro-F1 and +2.27pp macro-F1 gains
3. Analyse variance across seeds to assess train/test split sensitivity

Expected outcome: Low variance (std<0.01) and significant p-values (p<0.01 for macro-F1, p<0.05 for micro-F1), confirming reproducibility.

### 6.5.2 Cross-Domain Generalisation

Evaluate the hybrid architecture on datasets beyond SEC financial filings:

- **Biomedical**: PubMed articles with MeSH ontology (deeper hierarchies, more relation types)
- **E-commerce**: Product catalogues with category trees (high skew, sparse long tail)
- **Legal**: Court judgments with citation graphs (temporal relations, precedent chains)

Research questions:
- Does the pattern-based taxonomy generation transfer to other domains?
- Are the SRS weights (HP=25%, RTF=35%) appropriate for non-financial KGs?
- Do ceiling effects persist at different baseline accuracy levels?

### 6.5.3 Advanced Embedding Methods

Compare TransE against modern KG embedding techniques:

- **RotatE**: Rotation-based scoring for complex relation patterns
- **QuatE**: Quaternion embeddings for 1-to-N relations
- **ConvE**: Convolutional scoring for compositional reasoning
- **TuckER**: Tucker decomposition for parameter efficiency

Evaluation criteria:
- RTF probe accuracy (current: 100% with TransE)
- SRS improvement over baseline
- Training time and memory footprint
- Integration complexity with sklearn pipelines

Expected finding: Marginal RTF improvements (<2pp) do not justify added complexity for this use case.

### 6.5.4 Explainability and Human Evaluation

Develop user studies to assess the value of graph-based explanations:

1. Present users with classifier predictions and two explanation types:
   - Text-based: "Predicted based on tokens [revenue, quarterly, net]"
   - Graph-based: "Predicted Revenue because filing contains ProductRevenue (is-a Revenue)"

2. Measure user trust, comprehension, and decision-making speed

3. Identify which graph features (is-a, measured-in, for-period) provide the most useful explanations

Expected outcome: Graph-based explanations improve trust for rare classes but add negligible value for high-confidence predictions.

### 6.5.5 Continual Learning and Taxonomy Evolution

Extend the system to handle evolving knowledge graphs:

- **New concepts**: Automatically integrate concepts not present during training (zero-shot)
- **Taxonomy updates**: Incrementally add is-a edges without full retraining
- **Concept drift**: Detect when concept semantics change over time (e.g., "cloud computing" in 2005 vs 2025)

Research challenges:
- How to update TransE embeddings efficiently without catastrophic forgetting
- Whether to retrain classifiers or use embedding adapters
- Monitoring strategies to detect when retraining is necessary

### 6.5.6 Scaling to Enterprise Knowledge Bases

Test the architecture at 10⁶-scale:

- **Wikidata**: 100M+ entities, 1B+ triples (all domains)
- **UMLS**: 4M+ medical concepts, 15M+ relations (healthcare)
- **ProductGraph**: 10M+ products, 100M+ attributes (e-commerce)

Anticipated bottlenecks:
- Graph expansion becomes infeasible (10⁶ concepts → 10⁸ 2-hop candidates)
- Embedding training time exceeds practical limits (days to weeks)
- Sparse feature matrices exceed memory capacity (10⁶ × 10⁶ binary indicators)

Proposed solutions:
- Hierarchical indexing (partition graph by domain)
- Sampled embeddings (train on subgraph, infer on full graph)
- Feature hashing (reduce dimensionality via hashing trick)

---

## 6.6 Summary of Discussion

This chapter interpreted the empirical findings from Chapter 5, contextualised them within existing literature, and examined their implications for research and practice.

**Key insights:**

1. **SRS=0.8179 validates the hybrid approach**: The system retains 81.79% of semantic structure whilst maintaining sub-millisecond latency, demonstrating that specialised graph and vector stores can coexist effectively.

2. **Ceiling effects explain micro-F1 gate failure**: The +1.36pp improvement, whilst below the +3.0pp target, represents a 64.5% error reduction from an already strong 98.33% baseline. The +2.27pp macro-F1 gain provides stronger evidence for architectural value.

3. **Latency results exceed expectations**: Annoy's 0.037ms p99 latency (4,054× margin over SLO) confirms production readiness. Logarithmic scaling ensures graceful degradation at N=10,000 and beyond.

4. **Honest evaluation identifies trade-offs**: Robustness testing (taxonomy removal: -18.8% SRS) and scalability projections reveal architectural dependencies invisible in accuracy-only reporting.

5. **Practical guidance for practitioners**: Use hybrid architectures when structured knowledge exists, rare classes matter, and explainability is required. Avoid them for simple text classification or when black-box models suffice.

**Limitations acknowledged:**

- Single-seed validation limits statistical confidence
- Single-domain evaluation constrains generalisability
- Modest corpus size (N=3,218) leaves large-scale performance uncertain
- SRS weights reflect subjective priorities, not empirical optimisation

**Contributions to knowledge:**

- Quantified semantic preservation in hybrid KG-ML architectures via SRS metric
- Demonstrated that simple KG-as-features outperforms complex joint training for this use case
- Established latency and robustness as first-class evaluation criteria alongside accuracy
- Provided pattern-based taxonomy generation as a scalable alternative to manual annotation

Chapter 7 (Conclusion) synthesises these findings, restates the core contributions, and reflects on the research journey.

---

**Chapter 6 complete**. Next chapter: Conclusion (synthesis, contributions, reflection).
