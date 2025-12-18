# Chapter 1: Introduction

---

## 1.1 Motivation

Knowledge graphs have become foundational infrastructure for semantic search, question answering, and knowledge-intensive natural language processing tasks. By representing entities as nodes and relationships as typed, directed edges, knowledge graphs encode domain structure explicitly: "AccountsReceivable is-a CurrentAssets", "NetIncome measured-in USD", "Filing for-period 2024-Q3". This structured representation enables powerful reasoning capabilities—transitive closure over hierarchies, constraint checking via schema validation, and human-interpretable query results.

However, this expressiveness comes at a cost. Graph query engines (SPARQL, Cypher) require traversing adjacency structures at query time, limiting throughput to hundreds or thousands of queries per second on moderately sized graphs (10⁴–10⁵ entities). Approximate nearest neighbour search over vector embeddings, by contrast, delivers sub-millisecond latency at scales exceeding millions of entities through specialised indexing structures (Annoy, FAISS, ScaNN). Production retrieval systems—web search, recommendation engines, semantic similarity—overwhelmingly favour vector representations for this operational advantage.

The research community has responded by developing knowledge graph embeddings (TransE, RotatE, ComplEx) that map structured knowledge into continuous vector spaces. These methods promise "best of both worlds": semantic structure from graphs, operational performance from vectors. Yet a fundamental question remains empirically underexplored: **how much semantic structure is preserved during this transformation?**

Existing evaluations focus narrowly on link prediction accuracy or downstream task performance, treating embeddings as black boxes. A 2pp improvement in entity classification is reported as success, but whether the embedding retains hierarchical structure, preserves edge directionality, or distinguishes relation types remains unquantified. Production teams deploying hybrid graph-vector systems lack diagnostic tools to monitor semantic degradation, forcing architectural decisions based on accuracy alone.

This thesis addresses this gap by introducing the **Semantic Retention Score (SRS)**, a quantitative framework for measuring structural fidelity in hybrid knowledge graph-machine learning architectures. The metric combines four components—Hierarchy Presence (HP), Attribute Predictability (AtP), Asymmetry Preservation (AP), and Relation Type Fidelity (RTF)—to quantify what is lost when compressing rich graph structure into fixed-dimensional vectors.

The research evaluates a hybrid system on financial concept classification using SEC EDGAR filings, demonstrating that specialised graph stores and vector indices can coexist in production architectures whilst retaining 81.79% of semantic structure. The findings inform design decisions for practitioners and provide measurement tools for researchers.

---

## 1.2 Problem Statement

The integration of knowledge graphs with machine learning presents three interrelated challenges:

### 1.2.1 Semantic Preservation vs Operational Performance

Pure graph queries maintain semantic fidelity (SRS ≈ 1.0) but fail to meet production latency targets. SPARQL traversals over 10⁴ entities require tens to hundreds of milliseconds, violating interactive query budgets (<100ms user-perceived latency). Pure vector embeddings achieve sub-millisecond retrieval through approximate nearest neighbour methods but compress structured knowledge into continuous representations that lose hierarchical and directional information. Prior work demonstrates this trade-off qualitatively but lacks quantitative measurement.

### 1.2.2 Lack of Quantitative Semantic Diagnostics

Existing knowledge graph embedding evaluations prioritise link prediction (MRR, Hits@10) or downstream task accuracy (F1, precision/recall). These metrics measure predictive utility but not structural preservation. A system might achieve 95% classification accuracy whilst completely discarding hierarchical relationships, leaving practitioners unable to detect semantic loss until production failure. The field requires diagnostic metrics analogous to perplexity in language modelling or reconstruction error in autoencoders.

### 1.2.3 Integration Pattern Selection

Three architectural patterns dominate the literature: KG-as-features (concatenate graph signals with text embeddings), joint training (multi-task objectives combining graph and task losses), and retrieval-time routing (graph pre-filter followed by vector ranking). Each pattern involves trade-offs in complexity, interpretability, and performance. Existing comparisons focus on accuracy improvements over baselines, neglecting operational metrics (latency, memory, training time) and robustness properties (degradation under perturbations, sensitivity to data quality). Practitioners lack evidence-based guidance on when simple approaches suffice versus when complexity justifies cost.

This thesis investigates these challenges through a case study in financial concept classification, providing:
1. A quantitative framework (SRS) for measuring semantic preservation
2. Empirical comparison of integration patterns under operational constraints
3. Characterisation of architectural trade-offs through honest evaluation

---

## 1.3 Research Questions

The thesis addresses four research questions:

**RQ1 (Knowledge Fidelity)**: To what extent do lightweight KG signals improve semantic retention (measured by SRS) over text-only models?

- **Hypothesis H1**: Auto-generated taxonomy with pattern rules will increase Hierarchy Presence (HP) from baseline ~0% to ≥25% whilst maintaining AtP ≥ 95% and AP ≥ 99%, yielding SRS ≥ 0.75.
- **Rationale**: Pure text models (TF-IDF, BERT) lack explicit hierarchical structure, resulting in effective HP=0. Auto-taxonomy generation provides scalable hierarchy coverage without manual annotation. The 0.75 threshold represents a pragmatic balance: sufficient structure for downstream utility, achievable without exhaustive curation.

**RQ2 (Task Performance)**: When concatenated with text features, which KG representations (binary concept indicators vs minimal knowledge graph embeddings) deliver the best accuracy-latency trade-off?

- **Hypothesis H2**: Binary concept indicators (KG-as-features) will improve micro-F1 by ≥+3 percentage points over text-only baselines without violating latency budgets.
- **Rationale**: Prior work (Chen et al., 2024; Zhang et al., 2019) reports +2-5pp improvements for KG-augmented classification. Binary features are sparse, interpretable, and sklearn-compatible, avoiding GPU dependencies and training complexity of graph neural networks.

**RQ3 (Architecture Choice)**: Does a hybrid graph-vector infrastructure meet p95/p99 latency targets at 10³–10⁴ scale better than monolithic approaches?

- **Hypothesis H3**: Approximate nearest neighbour methods (Annoy, FAISS-HNSW) will achieve p99 < 150ms with 4,000× margin at target scale.
- **Rationale**: The 150ms threshold reflects interactive query requirements (100ms user-perceived + 50ms network/processing overhead). Logarithmic complexity (O(log N)) ensures graceful scaling. The 4,000× margin (p99 < 0.04ms) provides headroom for larger deployments.

**RQ4 (Honest Evaluation)**: Do robustness and scalability stress tests change which configuration appears "best" compared with accuracy-only reporting?

- **Hypothesis H4**: Under modest stressors (taxonomy removal, 5-10% unit noise), performance degradation will remain ≤10%, demonstrating system resilience.
- **Rationale**: Production systems encounter distributional shift, data quality issues, and infrastructure failures absent from clean research datasets. A configuration with 99% accuracy but 30% degradation under taxonomy removal is less production-ready than 98% accuracy with 5% degradation. Honest evaluation reveals these trade-offs.

---

## 1.4 Contributions

This thesis makes five primary contributions:

### 1.4.1 Semantic Retention Score (SRS) Metric

A quantitative framework for measuring structural fidelity in knowledge graph-to-vector transformations. The metric combines:
- **Hierarchy Presence (HP)**: Fraction of concepts with hierarchical context (is-a edges)
- **Attribute Predictability (AtP)**: Fraction with valid unit assignments (measured-in edges)
- **Asymmetry Preservation (AP)**: Fraction of directional edges without reverse pairs
- **Relation Type Fidelity (RTF)**: Probe classifier accuracy on relation prediction from embeddings

SRS provides an architectural diagnostic absent from prior work, enabling practitioners to monitor semantic degradation in production and researchers to compare embedding methods beyond link prediction benchmarks.

### 1.4.2 Pattern-Based Taxonomy Generation

A scalable method for auto-generating hierarchical relationships without manual annotation. The approach uses domain-specific pattern rules (e.g., "Current* is-a *", "Other* is-a *") combined with co-occurrence frequency analysis to generate 1,891 is-a edges, improving HP from 1.15% to 27.26%. This demonstrates that imperfect taxonomies (~90% estimated precision) provide sufficient inductive bias for downstream tasks, occupying a pragmatic middle ground between manual annotation (high precision, low scalability) and distant supervision (complex entity linking).

### 1.4.3 Ceiling Effect Characterisation

Empirical evidence that improvement targets must account for baseline strength. The research quantifies that absolute performance (99.68% micro-F1) and error reduction (64.5%) provide more informative measures than percentage-point gains when baselines exceed 98%. This challenges leaderboard culture in machine learning conferences, where +1.36pp improvements are dismissed as failures despite representing meaningful progress in high-accuracy regimes.

### 1.4.4 Honest Evaluation Framework

Operationalisation of robustness, scalability, and degradation testing alongside accuracy. The thesis evaluates:
- **Robustness**: Performance under perturbations (taxonomy removal: -18.8% SRS; unit noise: -7.0% SRS at 5% corruption)
- **Scalability**: Latency projections to 10× and 100× corpus sizes (logarithmic complexity validated empirically)
- **Degradation**: Identification of failure modes and fallback strategies

This three-pillar evaluation (accuracy + robustness + scalability) increases research-to-production transferability and builds practitioner confidence.

### 1.4.5 KG-as-Features Simplicity Advantage

Demonstration that sparse binary concept indicators outperform complex joint training for specific use cases. Whilst graph neural networks dominate the literature, this thesis shows that one-hot features achieve competitive performance (+1.36pp micro-F1, +2.27pp macro-F1) with zero GPU requirement, 10× faster training, perfect sklearn compatibility, and full interpretability. The research identifies conditions favouring simple approaches (high baselines, interpretability requirements, CPU-only inference) versus when GNN complexity justifies cost (low baselines, complex relational reasoning).

---

## 1.5 Scope and Limitations

### 1.5.1 Domain Scope

The research evaluates hybrid architectures on SEC EDGAR financial filings (N=3,218 documents, 47 US-GAAP concepts). This domain exhibits:
- High data quality (AtP=99.87% due to regulatory standardisation)
- Moderate hierarchy depth (3-4 levels: Assets → CurrentAssets → CashAndCashEquivalents)
- Heterogeneous relations (is-a, measured-in, for-period, reports)
- Strong text-only baseline (98.33% micro-F1)

Findings may not generalise to domains with different characteristics (deeper hierarchies, lower data quality, weaker baselines). However, the architectural patterns (specialisation principle, honest evaluation) and measurement tools (SRS) transfer across domains even if specific hyperparameters do not.

### 1.5.2 Methodological Scope

**Evaluation protocol**:
- Single dataset (SEC EDGAR), limiting cross-domain validation
- Single random seed (seed=42) for baseline, lacking statistical significance testing
- Modest corpus size (N=3,218), requiring analytical projections for larger-scale claims
- Multi-label classification task, not covering ranking, retrieval, or generation

**Integration patterns**:
- Three patterns evaluated (KG-as-features, joint training, hybrid routing)
- Focus on sklearn classifiers, not deep neural architectures (BERT, GPT)
- Binary concept indicators and TransE embeddings, not advanced methods (RotatE, GNNs)

**Acknowledged limitations**:
- SRS weights (HP=25%, RTF=35%) reflect design priorities, not empirical optimisation
- Auto-generated taxonomy has estimated 90% precision (heuristic validation, not gold standard)
- Ceiling effects at 98.33% baseline limit improvement measurement sensitivity

These limitations are discussed critically in Chapter 6 (Section 6.2) and inform future research directions (Section 6.5).

### 1.5.3 Out of Scope

**Not addressed**:
- Adversarial robustness (input perturbations, membership inference)
- Fairness and bias (protected attributes, disparate impact)
- Continual learning (evolving taxonomies, concept drift)
- Cross-lingual or cross-domain transfer
- Causal inference or counterfactual reasoning

Whilst important for production deployment, these topics exceed a single MSc thesis scope and represent distinct research agendas.

---

## 1.6 Thesis Structure

The remainder of this thesis is organised as follows:

**Chapter 2: Literature Review**
- Knowledge graph embedding methods (TransE, RotatE, ComplEx)
- KG-augmented machine learning (integration patterns, evaluation practices)
- Multi-modal learning (structured vs unstructured modality fusion)
- Gaps in quantitative semantic measurement

**Chapter 3: Methodology**
- Research design (hybrid architecture rationale, decision gates)
- Data collection (SEC EDGAR CompanyFacts, N=3,218 documents)
- SRS metric definition (component formulation, weight justification)
- Experimental protocol (train/test splits, hyperparameters, baselines)

**Chapter 4: Implementation**
- System architecture (graph store, vector index, classifier)
- Taxonomy generation algorithm (pattern rules, frequency analysis)
- Feature engineering pipeline (TF-IDF, concept indicators, embeddings)
- Technology stack (sklearn, TransE, Annoy, Neo4j)

**Chapter 5: Results**
- Decision gate outcomes (SRS, latency, micro-F1, macro-F1)
- Semantic retention analysis (HP, AtP, AP, RTF components)
- Classification performance (overall metrics, per-label analysis, error distribution)
- Latency and scalability (baseline results, projections, graph expansion overhead)
- Robustness evaluation (taxonomy removal, unit-noise tolerance)

**Chapter 6: Discussion**
- Interpretation of results (semantic retention, ceiling effects, scalability)
- Limitations and threats to validity (internal, external, construct)
- Implications for practice (when to use hybrid architectures, taxonomy generation strategies, deployment recommendations)
- Relationship to prior work (embeddings, KG-augmented ML, multi-modal learning)
- Future research directions (multi-seed validation, cross-domain generalisation, advanced embeddings, explainability, enterprise scale)

**Chapter 7: Conclusion**
- Research summary (RQ1-RQ4 findings)
- Contributions to knowledge (SRS, pattern-based taxonomy, ceiling effects, honest evaluation, KG-as-features simplicity)
- Practical implications (architectural decision framework, implementation recommendations, evaluation best practices)
- Reflection on research journey (successes, challenges, lessons learnt)
- Closing statement

**Appendices**
- A: Code Listings (key algorithms: taxonomy generation, SRS computation, baseline classifier)
- B: Full Metric Tables (per-label F1 scores, confusion matrices, latency distributions)
- C: Decision Gate Documentation (M3-M9 milestone reports, gate outcomes)
- D: Reproducibility Guide (environment setup, data pipeline, experiment scripts)

---

**Chapter 1 establishes the research context, problem space, questions, contributions, and scope. Chapter 2 positions the work within existing literature.**
