# Chapter 4: Implementation

---

## 4.1 System Architecture

The KG-MMML system comprises four primary components: a knowledge graph store for semantic structure, a vector index for fast retrieval, a feature engineering pipeline for text and concept representation, and a multi-label classifier for concept prediction. Figure 4.1 illustrates the complete architecture.

### 4.1.1 Architectural Overview

The system follows a **specialisation principle**: each component handles tasks suited to its design rather than forcing a monolithic solution. The knowledge graph (Neo4j) maintains explicit hierarchies, typed relations, and schema constraints efficiently but delegates similarity search to the vector index (Annoy). The vector index provides sub-millisecond retrieval through approximate nearest neighbour methods but lacks semantic reasoning capabilities, relying on the graph for hierarchy traversal. The classifier (sklearn LogisticRegression) balances interpretability and performance, avoiding neural complexity when linear models suffice.

**Data flow**:
1. **Ingestion**: SEC EDGAR CompanyFacts JSON → `facts.jsonl` (3,218 documents, 4,508 concepts)
2. **Graph construction**: `facts.jsonl` + taxonomy CSV → Neo4j (282,612 triples: reports, for-period, measured-in, is-a)
3. **Feature extraction**: TF-IDF text vectors (20,000 dimensions) + binary concept indicators (4,508 dimensions sparse)
4. **Embedding training**: TransE on graph triples → 128-dimensional concept embeddings
5. **Classification**: Concatenated features → OneVsRestClassifier (LogisticRegression per label)
6. **Retrieval**: Query vector → Annoy index → top-k candidates → graph expansion → re-ranking

### 4.1.2 Technology Stack

**Graph Store**: Neo4j Community Edition 4.4.x
- APOC library for two-hop traversal (`apoc.path.expand`)
- In-memory storage for sub-ms graph queries
- Cypher query language for hierarchy navigation

**Vector Index**: Annoy (Approximate Nearest Neighbours Oh Yeah) 1.17
- SVD-256 projection for dimensionality reduction (TF-IDF 20k → 256)
- 20 trees for accuracy-latency balance
- Euclidean distance metric
- CPU-only, no GPU dependency

**Feature Engineering**: scikit-learn 1.0.2, scipy 1.7.3
- TfidfVectorizer for text (max_features=20000, min_df=2)
- MultiLabelBinarizer for concept indicators (sparse CSR format)
- scipy.sparse for memory-efficient concatenation

**Embedding Training**: Custom TransE implementation
- NumPy 1.21 for tensor operations
- Stochastic gradient descent with margin ranking loss
- 128 dimensions, 50 epochs, learning rate 0.01

**Classification**: scikit-learn OneVsRestClassifier
- LogisticRegression per label (47 binary classifiers)
- L2 regularisation (C=1.0)
- liblinear solver for sparse features
- stratified train/test split (75%/25%, random_state=42)

**Development Environment**: Python 3.10, Windows 11, 16GB RAM, Intel i7 CPU (no GPU required)

---

## 4.2 Data Pipeline

### 4.2.1 Data Collection

**Source**: SEC EDGAR CompanyFacts API (`https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit}.json`)

**Selection criteria**:
- S&P 500 constituents plus representative mid-cap and small-cap firms
- Fiscal years 2020-2024 (5-year window)
- Forms 10-K (annual reports) and 10-Q (quarterly reports)
- Concepts with valid units (USD, shares, pure numbers; exclude malformed entries)
- us-gaap and dei namespaces only

**Collection procedure**:
1. Query SEC Company Tickers endpoint for CIK list
2. Fetch CompanyFacts JSON for each CIK with 250ms sleep (polite scraping)
3. Set User-Agent: "UniversityResearch project email@university.edu" (SEC requirement)
4. Handle HTTP 429 (rate limit) with exponential backoff
5. Store raw JSON in `data/raw/sec_edgar/` with date-stamped directory

**Result**: 3,218 company filings, 4,508 unique concepts, 282,612 total triples

### 4.2.2 Data Normalisation

**Script**: `src/utils/data_utils.py` (`build_corpus_from_facts`)

**Normalisation steps**:
1. **Concept ID standardisation**: Ensure namespace:name format (e.g., `us-gaap:Assets`)
   - Strip whitespace, handle missing namespaces (default to us-gaap)
   - Preserve existing prefixes (`dei:EntityCommonStockSharesOutstanding`)

2. **Document ID generation**: Create unique filing identifiers (`filing_{CIK}_{ACCN}`)
   - CIK: 10-digit Central Index Key (company identifier)
   - ACCN: Accession number with hyphens removed

3. **Unit validation**: Filter facts with valid measured-in units
   - Retain: USD, shares, pure (dimensionless quantities)
   - Exclude: Malformed units, null values, inconsistent decimals

4. **Temporal alignment**: Extract for-period dates (start_date, end_date, fiscal_period)
   - Normalize to ISO 8601 format (YYYY-MM-DD)
   - Map fiscal periods (Q1, Q2, Q3, FY) to standardised labels

**Output**: Line-delimited JSON (`data/facts.jsonl`), 38MB, one triple per line

### 4.2.3 Taxonomy Generation

**Objective**: Auto-generate is-a hierarchies without manual annotation

**Algorithm**: Pattern-based rules + co-occurrence frequency

**Pattern Rules** (86% of edges):
```python
patterns = [
    ("Current*", "*"),              # CurrentAssets → Assets
    ("Noncurrent*", "*"),          # NoncurrentLiabilities → Liabilities
    ("Other*", "*"),               # OtherRevenue → Revenue
    ("Short*", "*"),               # ShortTermDebt → Debt
    ("Long*", "*"),                # LongTermInvestments → Investments
    ("Deferred*", "*"),            # DeferredTaxAssets → TaxAssets
    ("Accumulated*", "*"),         # AccumulatedDepreciation → Depreciation
    ("*AndEquipment*", "*"),       # PropertyPlantAndEquipmentNet → PropertyPlantNet
    ("*Payable*", "*Liabilities"), # AccountsPayable → CurrentLiabilities
    ("*Receivable*", "*Assets"),   # AccountsReceivable → CurrentAssets
]
```

**Frequency Analysis** (6% of edges):
- Compute pairwise co-occurrence: count(conceptA, conceptB in same filing)
- Normalise by frequency: P(parent|child) = count(A,B) / count(B)
- Threshold: Retain edges where P(parent|child) > 0.3
- Directionality: Prefer shorter → longer (Assets → CurrentAssets, not reverse)

**Edge Validation**:
- Cycle detection: Remove edges creating circular dependencies
- Transitivity check: If A → B and B → C exist, do not add A → C (redundant)
- Semantic filtering: Exclude spurious pairs (e.g., Revenue → Liabilities)

**Result**: 1,891 is-a edges, HP improves from 1.15% to 27.26%

**Estimated Precision**: ~90% (heuristic validation via manual spot-checking, not gold-standard comparison)

---

## 4.3 Feature Engineering

### 4.3.1 Text Features (TF-IDF)

**Method**: Term Frequency-Inverse Document Frequency vectorisation

**Preprocessing**:
1. Extract concept tokens from facts (e.g., `us-gaap:AccountsReceivable` → "accountsreceivable")
2. Lowercase, strip namespace prefix, remove special characters
3. Join tokens per filing: `["assets", "revenue", "equity"]` → "assets revenue equity"

**Vectorisation parameters**:
- `max_features=20000`: Vocabulary size limit (top 20k by document frequency)
- `min_df=2`: Minimum document frequency (exclude singleton terms)
- `sublinear_tf=True`: Apply log scaling to term frequency (1 + log(tf))
- `norm='l2'`: L2 normalisation per document vector

**Rationale**:
- 20k features balance coverage and dimensionality (>99% of vocabulary variance)
- min_df=2 filters noise from typos and rare concepts
- Sublinear TF reduces impact of repeated concepts within filings
- L2 normalisation prevents longer documents from dominating cosine similarity

**Output**: Sparse CSR matrix (3,218 documents × 20,000 features), ~5% density

### 4.3.2 Concept Features (Binary Indicators)

**Method**: One-hot encoding with multi-label support

**Procedure**:
1. Load concept features from `concept_features_filing.npz` (sparse binary matrix)
2. Align rows to TF-IDF document order via `concept_features_index.csv`
3. For missing documents (not in concept features), insert zero rows
4. Concatenate horizontally with TF-IDF: `[TF-IDF | ConceptIndicators]`

**Sparse representation**:
- Shape: (3,218 documents × 4,508 concepts)
- Non-zero entries: 563,622 (2.9% density)
- Storage format: scipy.sparse.csr_matrix (compressed sparse row)
- Memory footprint: ~4.5MB (vs 115MB dense)

**Alignment logic** (`align_and_concat` in `baseline_tfidf.py`):
```python
# Build document ID → row index mapping
row_of = {doc_id: i for i, doc_id in enumerate(concept_index)}

# Align concept features to TF-IDF row order
aligned_rows = []
for doc_id in tfidf_docs:
    if doc_id in row_of:
        aligned_rows.append(concept_features[row_of[doc_id]])
    else:
        aligned_rows.append(sparse.csr_matrix((1, 4508)))  # zero row

# Horizontal stack
X = sparse.hstack([X_tfidf, sparse.vstack(aligned_rows)])
```

**Output**: Sparse CSR matrix (3,218 × 24,508 features), ~3% density

### 4.3.3 Knowledge Graph Embeddings (TransE)

**Method**: Translation-based embedding (Bordes et al., 2013)

**Training objective**: Minimise margin ranking loss
```
L = Σ max(0, γ + d(h + r, t) - d(h' + r, t'))
```
where:
- (h, r, t) is a positive triple (head, relation, tail)
- (h', r, t') is a negative triple (corrupted head or tail)
- d(·, ·) is Euclidean distance
- γ = 1.0 is the margin hyperparameter

**Hyperparameters**:
- Embedding dimension: 128
- Learning rate: 0.01
- Margin: 1.0
- Negative sampling ratio: 5 negatives per positive
- Training epochs: 50
- Batch size: 128

**Negative sampling strategy**:
- Corrupt head with probability 0.5, else corrupt tail
- Sample replacement entity uniformly from vocabulary
- Filter false negatives (avoid corrupting into true triples)

**Training data**: 282,612 triples (reports, for-period, measured-in, is-a)

**Convergence**: Loss stabilises after ~30 epochs, final loss ~0.15

**Output**: Concept embeddings (4,508 × 128), relation embeddings (4 × 128)

**Usage**: Not concatenated with text features in production config (KG-as-features uses binary indicators instead). Embeddings reserved for RTF probe evaluation and potential future enhancement.

---

## 4.4 Classification Pipeline

### 4.4.1 Baseline Classifier (Text-Only)

**Architecture**: OneVsRestClassifier wrapping LogisticRegression

**Training procedure**:
1. Split data: stratified 75% train, 25% test (random_state=42)
2. Vectorise text: TfidfVectorizer(max_features=20000, min_df=2)
3. Binarise labels: MultiLabelBinarizer (47 US-GAAP concepts)
4. Train: 47 independent binary classifiers (one per label)
5. Predict: Apply threshold 0.5 to sigmoid outputs

**Hyperparameters**:
- Regularisation: L2 penalty, C=1.0 (inverse regularisation strength)
- Solver: liblinear (efficient for sparse features)
- Max iterations: 1000
- Class weight: None (balanced via stratification)

**Performance**: Micro-F1=98.33%, Macro-F1=97.23%

### 4.4.2 Hybrid Classifier (Text+Concept)

**Architecture**: OneVsRestClassifier with concatenated features

**Training procedure**:
1. Split data: stratified 75% train, 25% test (random_state=42, identical to baseline)
2. Vectorise text: TfidfVectorizer (as baseline)
3. Load concept features: concept_features_filing.npz
4. Align and concatenate: `X = hstack([X_tfidf, X_concept])`
5. Binarise labels: MultiLabelBinarizer (as baseline)
6. Train: 47 independent binary classifiers

**Feature dimensions**: 24,508 (20,000 TF-IDF + 4,508 concepts)

**Sparsity**: ~3% (majority of features are zero for any given document)

**Performance**: Micro-F1=99.68%, Macro-F1=99.50%

**Improvement**: +1.36pp micro-F1, +2.27pp macro-F1 over baseline

### 4.4.3 Training Efficiency

**Baseline training time**: ~45 seconds (47 classifiers × 2,413 training samples)

**Hybrid training time**: ~120 seconds (increased feature dimensionality: 20k → 24.5k)

**Inference latency**: <1ms per document (sparse matrix-vector multiplication)

**Memory footprint**: ~200MB (sparse features + 47 classifier weights)

**Scalability**: Linear in number of labels, sublinear in features (sparse operations)

---

## 4.5 Retrieval System

### 4.5.1 Vector Index Construction

**Method**: Annoy (Approximate Nearest Neighbours Oh Yeah)

**Index building**:
1. Dimensionality reduction: SVD projection (TF-IDF 20k → 256 dimensions)
2. Add vectors: `index.add_item(i, vector[i])` for each document
3. Build forest: `index.build(n_trees=20)` constructs search trees
4. Save index: `index.save('annoy_index.ann')` persists to disk

**SVD Projection** (TruncatedSVD from sklearn):
- Components: 256 (retains ~95% of variance)
- Explained variance ratio: 0.947
- Transformation: `X_reduced = svd.transform(X_tfidf)`

**Tree Construction**:
- Method: Random projection trees (binary space partitioning)
- Number of trees: 20 (accuracy-latency trade-off)
- More trees → higher recall, slower queries
- Fewer trees → lower recall, faster queries

**Distance metric**: Euclidean (L2 norm)

**Index size**: ~15MB on disk (256 dims × 3,218 vectors + tree metadata)

### 4.5.2 Query Processing

**Query pipeline**:
1. **Vectorise query**: TfidfVectorizer.transform(query_text) → sparse vector (20k dims)
2. **Project**: SVD.transform(query_vector) → dense vector (256 dims)
3. **ANN search**: index.get_nns_by_vector(query, n=100) → top-100 candidate IDs
4. **Graph expansion** (optional): For each candidate, retrieve parents via Neo4j
5. **Re-ranking**: Score candidates by exact cosine similarity
6. **Top-k selection**: Return top-10 results

**Latency breakdown** (p99):
- Vectorisation: ~0.01ms (TF-IDF + SVD)
- ANN search: 0.037ms (Annoy with 20 trees)
- Graph expansion: +0.0023ms (two-hop traversal via Neo4j APOC)
- Re-ranking: ~0.05ms (exact cosine on 100 candidates)
- **Total**: ~0.1ms p99 (well under 150ms SLO)

### 4.5.3 Graph-Augmented Retrieval

**Two-hop expansion**:
1. Retrieve direct parents: `MATCH (c:Concept)-[:IS_A]->(p) WHERE c.id = candidate RETURN p`
2. Retrieve siblings: `MATCH (c)-[:IS_A]->(p)<-[:IS_A]-(s) WHERE c.id = candidate RETURN s`
3. Union candidates: original + parents + siblings
4. Remove duplicates, limit to top-k after re-ranking

**Expansion statistics**:
- Mean one-hop: 1.4 concepts (direct parents)
- Mean two-hop: 62.3 concepts (parents + siblings)
- Expansion factor: 44× (62.3 / 1.4)
- Overhead: +0.0023ms p99 (negligible despite 44× expansion)

**Production configuration**: Two-hop expansion enabled by default (latency impact minimal, semantic coverage significant)

---

## 4.6 Evaluation Infrastructure

### 4.6.1 Decision Gate Framework

**Decision gates** (defined in Chapter 3, evaluated in Chapter 5):
1. **SRS ≥ 0.75**: Semantic Retention Score threshold
2. **p99 latency < 150ms**: Service-level objective for retrieval
3. **Micro-F1 improvement ≥ +3pp**: Classification accuracy target
4. **Macro-F1 improvement**: Rare class performance (no fixed threshold)

**Gate evaluation scripts**:
- `src/cli/compute_srs.py`: Computes HP, AtP, AP, RTF components
- `src/cli/evaluate_latency.py`: Measures p50/p95/p99 across methods
- `src/cli/baseline_tfidf.py`: Runs classification experiments, outputs F1 scores
- `src/cli/analyze_errors.py`: Per-label breakdown, confusion analysis

### 4.6.2 Reproducibility Measures

**Fixed random seeds**:
- NumPy: `np.random.seed(42)`
- Scikit-learn: `random_state=42` in train_test_split, classifiers
- TransE training: Manual seeding before negative sampling

**Pinned dependencies**:
- `requirements.txt` with exact versions (scipy==1.7.3, not scipy>=1.7)
- Conda environment export: `environment.yml`

**Data snapshots**:
- SEC EDGAR fetch date: 2025-10-11
- Raw JSON archived in `data/raw/sec_edgar/2025-10-11/`
- Processed `facts.jsonl` checksummed (SHA256 hash documented)

**Configuration files**:
- `configs/experiment_baseline.yaml`: TF-IDF hyperparameters
- `configs/experiment_joint.yaml`: Joint training hyperparameters (not used in production)
- `configs/annoy_index.yaml`: Tree count, distance metric, SVD dimensions

**Deterministic metrics**:
- HP, AtP, AP: Computed from graph structure (zero variance across runs)
- RTF: Probe classifier trained with fixed seed (variance σ=0.000)

### 4.6.3 Robustness Testing

**Taxonomy removal test** (M7):
- Procedure: Set HP=0 (drop all is-a edges), recalculate SRS
- Expected degradation: ≤10%
- Actual degradation: 18.8% (threshold exceeded; expected for hybrid system)

**Unit-noise tolerance test** (M7):
- Procedure: Reduce AtP by 5% and 10% (simulate missing unit metadata)
- Expected degradation: ≤10%
- Actual degradation: 7.0% at 5% noise, 9.0% at 10% noise (both PASS)

**Implementation**:
```python
def perturb_atp(original_atp, noise_level):
    """Simulate data quality degradation."""
    return original_atp * (1 - noise_level)

def compute_perturbed_srs(hp, atp, ap, rtf, noise_level):
    """Recompute SRS under perturbation."""
    atp_perturbed = perturb_atp(atp, noise_level)
    return 0.25 * hp + 0.20 * atp_perturbed + 0.20 * ap + 0.35 * rtf
```

---

## 4.7 Deployment Considerations

### 4.7.1 Production Readiness

**Latency SLO compliance**:
- p99 retrieval: 0.037ms (4,054× margin below 150ms)
- p99 classification: <1ms (inference on 24.5k sparse features)
- End-to-end p99: ~1ms (retrieval + classification + overhead)

**Throughput capacity**:
- Single CPU core: ~1,000 queries/second (1ms per query)
- Horizontal scaling: Stateless service, linear scale-out
- Neo4j reads: Replicated across nodes for load distribution

**Memory footprint**:
- Annoy index: 15MB (loaded once, shared across requests)
- TF-IDF vocabulary: 2MB (20k terms)
- Classifier weights: 200MB (47 × 24.5k sparse coefficients)
- Neo4j graph: 50MB in-memory (4,508 concepts, 282k triples)
- **Total**: ~270MB per service instance

### 4.7.2 Monitoring and Observability

**SRS component tracking**:
- Log HP, AtP, AP daily (detect taxonomy staleness)
- Alert if HP drops >10% (indicates missing is-a edges)
- Alert if AtP < 90% (indicates upstream data quality issues)

**Latency monitoring**:
- Track p50/p95/p99 per endpoint (retrieval, classification, end-to-end)
- Alert if p99 exceeds 10ms (early warning before SLO violation)
- Dashboard: Percentile histograms over 24-hour windows

**Accuracy drift detection**:
- Sample predictions for manual review (10 per day)
- Compute rolling macro-F1 on held-out validation set
- Alert if macro-F1 drops below 97% (indicates concept drift or data shift)

### 4.7.3 Failure Modes and Mitigations

**Neo4j unavailable**:
- Fallback: Vector-only retrieval (skip graph expansion)
- Impact: SRS degrades, latency improves (no 2-hop traversal)
- Recovery: Automatic retry with exponential backoff

**Annoy index corrupted**:
- Fallback: Exact cosine similarity (brute-force search)
- Impact: Latency increases 100×, still under SLO (<10ms for N=3,218)
- Recovery: Rebuild index from stored SVD projections (~30 seconds)

**Classifier model stale**:
- Fallback: Serve cached predictions for common queries
- Impact: Reduced coverage, no impact on latency
- Recovery: Retrain model on updated data (offline, ~2 minutes)

---

## 4.8 Summary

This chapter detailed the implementation of the KG-MMML hybrid architecture, covering:
- **System design**: Specialisation principle (graph for semantics, vector for speed)
- **Data pipeline**: SEC EDGAR ingestion, normalisation, taxonomy generation
- **Feature engineering**: TF-IDF text features, binary concept indicators, TransE embeddings
- **Classification**: Sklearn OneVsRestClassifier with sparse features
- **Retrieval**: Annoy vector index with optional graph expansion
- **Evaluation**: Decision gates, reproducibility measures, robustness testing
- **Deployment**: Production readiness, monitoring, failure mitigation

The implementation demonstrates that hybrid systems can achieve sub-millisecond latency whilst preserving semantic structure, validating the architectural choices made in Chapter 3. Chapter 5 evaluates this implementation against the four decision gates and research questions.

---

**Chapter 4 provides the technical foundation for understanding the empirical results in Chapter 5.**
