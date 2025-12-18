# Chapter 2: Literature Review

---

## 2.1 Introduction

This chapter positions the research within the existing body of knowledge on knowledge graph embeddings, KG-augmented machine learning, and multi-modal learning systems. The review critically examines integration methods, identifies gaps in quantitative semantic measurement, and establishes the theoretical foundation for the Semantic Retention Score (SRS) metric introduced in Chapter 3.

Multi-modal models align information from text, images, audio, video and tabular signals. Knowledge graphs encode entities, relations, hierarchies and constraints. Intuitively, the two are complementary: KGs provide explicit structure and provenance; multi-modal learning provides perceptual generalisation and cross-modal alignment. However, integration remains uneven. Many systems append KG embeddings to neural features and claim to be "knowledge-aware", without demonstrating that directionality, hierarchy or cardinality survive the conversion to vectors (Chen et al., 2024).

This review addresses three research domains: (1) knowledge graph embedding methods and their limitations, (2) integration patterns for KG-augmented machine learning, and (3) evaluation practices in multi-modal systems. Throughout, the focus is on identifying what is lost during graph-to-vector transformation and how to measure this loss quantitatively.

---

## 2.2 Knowledge Graphs: Contributions and Risks

### 2.2.1 Four Concrete Contributions

Knowledge graphs add four distinct capabilities to machine learning systems (Ji et al., 2022; Nickel et al., 2016):

**1. Typed entities.** Nodes provide named concepts—products, parts, species, artworks, chemicals, events—anchoring multi-modal signals to a controlled vocabulary and preventing synonym sprawl. In financial domains, typed entities distinguish "Assets" (balance sheet category) from "AssetTurnover" (efficiency ratio), enabling precise retrieval.

**2. Relations and constraints.** Edges encode asymmetry (used-for, causes), hierarchy (is-a, part-of), and composition. These curb the symmetry bias of many contrastive spaces (Baltrušaitis et al., 2019). The is-a relation "CashAndCashEquivalents → CurrentAssets → Assets" is inherently directional; flattening into bidirectional similarity loses this constraint.

**3. Compositional reasoning.** Paths (e.g., tool → used-for → cutting; painting → created-by → artist → active-in → period) enable chained filtering and retrieval beyond nearest-neighbour similarity. Graph traversal supports queries like "find all revenue concepts measured in USD for Q3 2024", which pure vector search cannot satisfy without external filtering.

**4. Interpretability and auditability.** Paths and types produce human-readable rationales. Explanations can cite entities and relations, not only heatmaps or token attributions (Das et al., 2020). This is critical for regulatory compliance applications where audit trails must be transparent.

### 2.2.2 Four Risks

Despite these advantages, knowledge graph integration introduces risks that practitioners must measure rather than assume away:

**Semantic loss.** When discrete relations are compressed into continuous vectors, directionality and one-to-many patterns flatten into proximity (Nickel et al., 2016). The relation "AccountsReceivable → CurrentAssets" and its reverse "CurrentAssets → AccountsReceivable" become indistinguishable in symmetric embedding spaces.

**Coverage gaps.** Generic KGs lack domain-critical edges; domain drift across organisations and time creates staleness (Paulheim, 2017). A knowledge graph built from IFRS taxonomies will not cover US-GAAP-specific concepts, limiting transferability.

**Staleness and bias.** Multi-modal data amplify skew via nearest-neighbour effects (Mehrabi et al., 2021). If training data over-represents technology sector filings, the embedding space will bias retrieval towards tech-specific financial concepts.

**Operational overhead.** Keeping graph facts, embeddings and indices consistent under streaming updates requires careful synchronisation (Trivedi et al., 2017). Production systems must reconcile graph edits with re-indexed embeddings, introducing latency and consistency challenges.

**Critical insight:** A rigorous approach treats semantic preservation and operational realism as outcomes to measure, not assumptions. This motivates the SRS metric (Chapter 3) and honest evaluation framework (Chapter 5).

---

## 2.3 Knowledge Graph Embedding Methods

### 2.3.1 Translational Models

**TransE** (Bordes et al., 2013) represents the foundational translational embedding method. It models relations as translations in embedding space: h + r ≈ t, where h (head entity), r (relation), and t (tail entity) are d-dimensional vectors. The model optimises embeddings to minimise ‖h + r − t‖ for observed triples whilst maximising distance for corrupted negatives.

**Strengths:** Simple, efficient, effective for one-to-one relations (e.g., capital-of, measured-in).

**Limitations:** Struggles with one-to-many (Assets → {CurrentAssets, NoncurrentAssets}), many-to-one, and many-to-many relations. Symmetric relations (co-occurs-with) cannot be modelled accurately since h + r = t implies t + r = h (Nickel et al., 2016).

**RotatE** (Sun et al., 2019) addresses TransE limitations by modelling relations as rotations in complex space: h ◦ r ≈ t, where ◦ denotes element-wise Hadamard product. This enables modelling of symmetric, antisymmetric, inversion and composition patterns.

### 2.3.2 Semantic Matching Models

**DistMult** (Yang et al., 2015) uses a bilinear scoring function: score(h, r, t) = h^T diag(r) t. This models symmetric relations naturally but cannot capture asymmetry (is-a, part-of).

**ComplEx** (Trouillon et al., 2016) extends DistMult to complex embeddings, enabling asymmetric modelling through Hermitian products. It demonstrates state-of-the-art performance on link prediction benchmarks (FB15k-237, WN18RR).

### 2.3.3 Graph Neural Networks

**Graph Convolutional Networks (GCNs)** (Kipf and Welling, 2017) and **Graph Attention Networks (GATs)** (Veličković et al., 2018) learn node representations by aggregating information from multi-hop neighbourhoods. These methods excel at node classification and link prediction but require message-passing at inference time, increasing latency.

**Limitation for this research:** GNN inference latency (10-50ms for 2-3 hop aggregation) violates the p99 < 150ms service-level objective for interactive retrieval systems. This motivates the KG-as-features approach (binary concept indicators) which provides O(1) feature extraction.

### 2.3.4 Gap in the Literature

Existing evaluations focus on **link prediction accuracy** (MRR, Hits@10) or **downstream task performance** (F1, precision/recall). These metrics measure predictive utility but not structural preservation (Wang et al., 2017). A system might achieve 95% classification accuracy whilst completely discarding hierarchical relationships, leaving practitioners unable to detect semantic loss until production failure.

**Research gap addressed by this thesis:** The field requires diagnostic metrics analogous to perplexity in language modelling or reconstruction error in autoencoders—quantitative measures of semantic fidelity independent of downstream accuracy.

---

## 2.4 KG-Augmented Machine Learning: Integration Patterns

The literature reveals three dominant integration patterns, each with distinct trade-offs (Chen et al., 2024; Zhang et al., 2019).

### 2.4.1 KG-as-Features (Pre-computed Embeddings)

**Mechanism.** Train a KGE model (TransE, ComplEx) on the knowledge graph; concatenate entity/edge embeddings with text or image features; train a lightweight classification head.

**Strengths.** Minimal engineering complexity; fast inference (O(1) feature lookup); convenient ablations. Useful for candidate generation when attributes align directly with textual cues (Marino et al., 2017).

**Weaknesses.** Weak retention of directionality and hierarchy; embeddings drift as graphs and encoders evolve; brittle out-of-distribution behaviour. Performance gains can reflect label co-occurrence rather than genuine knowledge use (García-Durán and Niepert, 2018).

**Decision rule (from literature).** A necessary baseline, valuable for candidate generation, but insufficient for strong claims of knowledge-aware reasoning. Deploy only if semantic retention score (SRS) meets predefined threshold.

**Application to financial classification:** Binary concept indicators (one-hot encoding of concept presence) provide an even simpler variant: no embedding training required, perfect interpretability (feature=concept), and sparse representation suitable for sklearn classifiers. This trades embedding expressiveness for transparency and operational simplicity.

### 2.4.2 Joint KG-MM Objectives

**Mechanism.** Learn a shared embedding space for entities and multi-modal features with graph-aware constraints: parents closer than non-ancestors; asymmetric relations remain directional; salient attributes reconstructible from entity vectors (Liu et al., 2021; Wang et al., 2020).

**Strengths.** Better semantic fidelity; improved handling of fine-grained hierarchies; more faithful rationales (Zhou et al., 2020).

**Weaknesses.** Heavier training (3-4× longer than baseline); unstable optimisation if losses proliferate; sensitive to coverage gaps; increased complexity for end-to-end reproduction (Yao et al., 2019).

**Decision rule (from literature).** Use when faithful relations matter (explanation, auditing, long-tail classes). Keep constraints minimal and interpretable: hierarchy preservation, asymmetry constraints, attribute reconstruction. Avoid over-engineered multi-term loss functions.

**Evidence from prior work:** Zhang et al. (2019) report +2-5pp F1 improvements on cross-modal retrieval when using joint training with hierarchy constraints. However, Marino et al. (2017) found that gains diminish when baselines exceed 95% accuracy—the ceiling effect problem addressed in this thesis.

### 2.4.3 Retrieval-time Knowledge Routing (Hybrid Architectures)

**Mechanism.** At inference, route queries through a graph store for structural filtering and rationale paths, and a vector index for dense similarity search; fuse ranks; cache rationales and hot subgraphs; stream updates to keep components synchronised (Krishna et al., 2017).

**Strengths.** Specialisation yields superior scale and latency; instrumentation is straightforward; explanations are first-class (graph paths), not post-hoc (Radford et al., 2021).

**Weaknesses.** More moving parts; eventual consistency across stores; requires clear playbooks for fall-backs and reconciliation.

**Decision rule (from literature).** The most operationally credible pattern for production retrieval and discovery portals. Adopt when two-hop-plus-vector queries exceed p95 latency budget in monolithic stores.

**Technology examples:** Neo4j (graph database) + Annoy/FAISS (vector index) + Redis (cache) + Kafka (stream). This mirrors architectures used by LinkedIn (economic graph), Amazon (product knowledge graph), and Google (Knowledge Graph + neural retrieval).

---

## 2.5 Multi-Modal Learning and Semantic Alignment

### 2.5.1 Contrastive Learning Foundations

**CLIP** (Radford et al., 2021) demonstrated that contrastive learning over 400M image-text pairs produces embeddings aligned across modalities. The key insight: maximise cosine similarity for matched (image, caption) pairs whilst minimising similarity for mismatched pairs.

**Limitation for structured knowledge:** Pure contrastive spaces are symmetric (similarity is bidirectional) and lack explicit type constraints. The relation "Revenue → OperatingIncome" (hierarchical, asymmetric) becomes indistinguishable from "Revenue co-occurs-with OperatingIncome" (symmetric association).

### 2.5.2 Multi-Resolution Representations

**Principle (from literature review).** Do not crush all semantics into a single vector. Maintain layered representations and escalate by need:
- **Type layer:** categories and attributes (entity types, units, periods)
- **Direct-relation layer:** immediate edges with direction (is-a, measured-in, for-period)
- **Neighbourhood layer:** k-hop summaries for context
- **Full-semantics layer:** path extraction for explanation and adjudication

**Query strategy:** Generate candidates with vectors; verify with direct relations; explain with paths on demand. This preserves meaning whilst meeting latency budgets (Krishna et al., 2017).

### 2.5.3 Application Contexts

The literature demonstrates KG-MMML integration across diverse domains (Chen et al., 2024):

- **Retail visual search:** Query "espadrille wedge sandal with ankle strap"; KG encodes is-a and has-attribute relations
- **Manufacturing inspection:** Query "fatigue crack near rivet"; KG encodes part-of and failure-mode relations
- **Cultural heritage:** Query "impressionist landscape with cathedral"; KG encodes created-by, style, depicts relations
- **Scientific media:** Query "fluorescence micrograph of checkpoint proteins"; KG encodes interacts-with, located-in, process-part-of relations

**Financial concept classification (this thesis):** Query "current assets reported in 10-K FY2024"; KG encodes is-a (CashAndCashEquivalents → CurrentAssets), measured-in (USD), for-period (FY2024), reports (Filing → Concept) relations.

Across these domains, long-tail phenomena, hierarchy depth and asymmetric relations make structured knowledge valuable—yet only if preserved and operational at scale.

---

## 2.6 Evaluation Practices and Honest Assessment

### 2.6.1 The Accuracy-Only Problem

Existing research overwhelmingly evaluates KG-MMML systems using downstream task accuracy: F1 score, precision/recall, mean average precision (mAP), or Hits@K (Ji et al., 2022; Wang et al., 2017). These metrics measure **predictive utility** but not **structural preservation**.

**Critical limitation:** A system might achieve 99% classification accuracy whilst completely discarding hierarchical relationships. The knowledge graph becomes mere label co-occurrence, adding no semantic value beyond statistical correlation (García-Durán and Niepert, 2018).

### 2.6.2 Proposed Evaluation Dimensions (Literature Review)

The literature review proposes six evaluation dimensions for honest assessment:

1. **Effectiveness:** Retrieval/zero-shot metrics on in-domain and shifted distributions
2. **Semantic retention:** AtP/HP/AP/RTF components (novel contribution)
3. **Efficiency:** p50/p95/p99 latency, memory, index-build times, update lag
4. **Robustness:** Modality dropout, label noise, distribution shift, class imbalance
5. **Reproducibility:** Seeds, configs, budgets, spread (mean/SD, min/max)
6. **Interpretability:** Rationale precision and counterfactual sensitivity

**Gap in practice:** Most papers report (1) only. State-of-the-art KG embedding papers (ComplEx, RotatE) focus exclusively on link prediction MRR and Hits@10, neglecting semantic fidelity, latency, robustness and interpretability (Nickel et al., 2016; Sun et al., 2019).

### 2.6.3 Benchmark Myopia

Static leaderboards (FB15k-237, WN18RR, YAGO3-10) hide brittleness under distribution shift. Paulheim (2017) demonstrates that knowledge graph refinement methods optimised for clean benchmarks fail when deployed on noisy enterprise graphs with 10-30% incorrect edges.

**Recommendation from literature:** Include stress tests on scale, skew, shift and noise; publish degradation curves and tail-latency distributions, not just mean accuracy (Mehrabi et al., 2021).

---

## 2.7 Common Pitfalls and Design Principles

The literature review identifies five recurring failures:

1. **Interpretability theatre.** Attractive graph overlays that do not affect predictions when removed are decorative, not explanatory. Require faithful rationales whose ablation changes outputs (Das et al., 2020).

2. **Benchmark myopia.** Static leaderboards hide brittleness. Include stress tests on scale, skew, shift and noise (Paulheim, 2017).

3. **One-store absolutism.** Forcing topology and dense similarity into one database invites slow queries or impoverished semantics. Specialise and route (Krishna et al., 2017).

4. **Generic-KG complacency.** Breadth without critical relations is a liability. Measure relation criticality; invest where returns are highest (Chen et al., 2024).

5. **Over-engineered loss functions.** Many-term joint objectives can be unstable and hard to reproduce. Keep constraints minimal and interpretable (Liu et al., 2021).

**Design principle adopted in this thesis:** Specialisation over generalisation. Use purpose-built components (graph for structure, vector for similarity) with clear service-level objectives and operational fall-backs.

---

## 2.8 Gaps Addressed by This Research

The literature review reveals four critical gaps:

### Gap 1: Quantitative Semantic Measurement

**Problem:** Existing work lacks metrics for measuring what is lost during graph-to-vector transformation. Link prediction accuracy (MRR, Hits@10) measures predictive utility, not structural fidelity.

**This thesis contribution:** The Semantic Retention Score (SRS) with four components—Hierarchy Presence (HP), Attribute Predictability (AtP), Asymmetry Preservation (AP), Relation Type Fidelity (RTF)—provides the first quantitative framework for measuring semantic loss.

### Gap 2: Pattern-Based Taxonomy Generation

**Problem:** Manual taxonomy curation does not scale; distant supervision via entity linking introduces noise and complexity (Paulheim, 2017).

**This thesis contribution:** Auto-taxonomy generation using conservative pattern rules (e.g., "Current* → CurrentAssets") combined with frequency analysis achieves 27.26% hierarchy coverage without manual annotation, occupying a pragmatic middle ground.

### Gap 3: Ceiling Effect Characterisation

**Problem:** Improvement targets ignore baseline strength. At 98%+ accuracy, +1pp gains are dismissed as failures despite representing meaningful progress (Marino et al., 2017).

**This thesis contribution:** Empirical evidence that absolute performance and error reduction provide more informative measures than percentage-point gains in high-accuracy regimes.

### Gap 4: Operational Realism in Evaluation

**Problem:** Most papers report accuracy on clean benchmarks, neglecting latency, robustness and degradation under perturbations (Ji et al., 2022).

**This thesis contribution:** Honest evaluation framework combining accuracy, semantic retention (SRS), latency (p50/p95/p99), and robustness (taxonomy removal, unit noise) with documented decision gates.

---

## 2.9 Theoretical Foundation for This Thesis

The literature review establishes three theoretical pillars:

**Pillar 1: Multi-Resolution Semantics**
Knowledge cannot be flattened into a single vector without loss (Nickel et al., 2016). This thesis implements multi-resolution representations: type layer (categories), direct-relation layer (is-a, measured-in), neighbourhood layer (concept co-occurrence), and full-semantics layer (graph paths).

**Pillar 2: Hybrid Specialisation**
Monolithic architectures sacrifice either semantic fidelity (pure vector) or operational performance (pure graph). Hybrid architectures (graph + vector + cache + stream) deliver both through specialisation (Krishna et al., 2017; Radford et al., 2021).

**Pillar 3: Honest Evaluation**
Accuracy-only reporting hides brittleness, semantic loss and operational failures. This thesis operationalises six evaluation dimensions (effectiveness, semantic retention, efficiency, robustness, reproducibility, interpretability) as documented decision gates (Mehrabi et al., 2021; Paulheim, 2017).

---

## 2.10 Summary

This literature review establishes that:

1. **Knowledge graphs add value** through typed entities, directional relations, compositional reasoning and interpretability—but only if these properties survive integration (Ji et al., 2022; Nickel et al., 2016).

2. **Existing embedding methods** (TransE, ComplEx, GNNs) optimise for link prediction accuracy, not semantic preservation, leaving practitioners unable to detect structural loss (Wang et al., 2017).

3. **Three integration patterns** dominate: KG-as-features (simple, fast, weak semantics), joint objectives (better fidelity, heavier training), and hybrid routing (operationally credible, complex) (Chen et al., 2024; Zhang et al., 2019).

4. **Evaluation practices** focus narrowly on accuracy, neglecting semantic retention, latency, robustness and interpretability—the honest evaluation gap (Das et al., 2020; Paulheim, 2017).

5. **Four research gaps** motivate this thesis: quantitative semantic measurement (SRS), scalable taxonomy generation (auto-taxonomy), ceiling effect characterisation, and operational realism in evaluation.

**Chapter 3 (Methodology) operationalises these insights into a concrete research design with measurable decision gates, positioning the work as a critical response to the literature's accuracy-only culture.**

---

**References for this chapter are consolidated in the Bibliography section at the end of the thesis.**
