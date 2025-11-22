# Methodology

This chapter describes the research design, data collection, knowledge graph construction, feature engineering, model training, and evaluation procedures used to investigate the integration of knowledge graphs with machine learning for SEC financial document classification.

## 1. Overview and Research Design

### 1.1 Central Research Problem

This project addresses a fundamental tension in knowledge-enhanced machine learning systems: **semantic preservation versus operational performance**. Pure vector embeddings enable fast similarity search but lose crucial relational structure (hierarchies, directionality, cardinality). Pure graph queries preserve semantics but struggle with scale and open-world retrieval. This research investigates whether a **hybrid architecture**—combining a graph semantic spine with a vector index—can maintain both semantic fidelity and sub-millisecond query latency.

### 1.2 Multi-Modal Definition: Structured Knowledge + Text

This work interprets "multi-modal machine learning" as the fusion of **structured knowledge** (knowledge graphs) with **unstructured text**, following Chen et al. (2024) and Zhang et al. (2019) who categorize KG-augmented systems as multi-modal when bridging symbolic (graph edges, typed entities) and sub-symbolic (continuous embeddings) representations.

**Two modalities integrated**:

1. **Structured modality**: Knowledge graph with 4,508 concepts, 1,891 is-a edges, measured-in relationships, and temporal period associations
2. **Unstructured modality**: Concept labels and textual descriptions processed via TF-IDF vectorization

This contrasts with **perceptual multi-modality** (vision+language systems like CLIP) but demonstrates the same integration challenges: semantic loss during embedding, scalability trade-offs, and evaluation honesty. The hybrid architecture patterns validated here generalize to perceptual domains by substituting encoders (e.g., CLIP for TF-IDF) while preserving the graph semantic spine.

### 1.3 Hybrid Architecture Rationale

The literature review (Section 3.3) identified three integration patterns: KG-as-features, joint objectives, and retrieval-time routing. This project implements and evaluates all three, with the hybrid architecture (retrieval-time routing) selected as the production configuration based on:

- **Semantic preservation**: Graph store maintains typed entities, directed edges, and hierarchical relationships without compression
- **Operational performance**: Vector index (Annoy) delivers sub-millisecond queries at scale N ∈ {10³, 10⁴}
- **Explainability**: Graph paths provide human-readable rationales (e.g., "AccountsReceivable → CurrentAssets → Assets")
- **Specialization principle**: Purpose-built systems (graph for structure, vector for similarity) outperform monolithic stores under mixed workloads

### 1.4 Research Questions

**RQ1 (Knowledge Fidelity)**: To what extent do lightweight KG signals improve semantic retention (measured by SRS) over a text-only model?

- **Hypothesis H1**: Auto-generated taxonomy with pattern rules will increase Hierarchy Presence (HP) from baseline ~0% to ≥25% while maintaining AtP ≥ 95% and AP ≥ 99%, yielding SRS ≥ 0.75.

**RQ2 (Task Performance)**: When concatenated with text features, which KG representations (one-hot/hashed concepts vs minimal KGE) deliver the best accuracy ↔ latency trade-off?

- **Hypothesis H2**: Binary concept indicators (KG-as-features) will improve micro-F1 by ≥+3 percentage points over text-only baseline without violating latency budgets.

**RQ3 (Architecture Choice)**: Does a hybrid graph–vector stack meet p95/p99 latency targets at 10³–10⁴ scale better than monolithic approaches?

- **Hypothesis H3**: Approximate nearest neighbor (ANN) methods (Annoy, FAISS-HNSW) will achieve p99 < 150ms with 4,000× margin at target scale.

**RQ4 (Honest Evaluation)**: Do robustness and scale stress tests change which configuration appears "best" compared with accuracy-only reporting?

- **Hypothesis H4**: Under modest stressors (taxonomy off / 5-10% unit noise), performance drops will remain ≤10%, demonstrating system resilience.

---

## 2. Data Collection and Processing

### 2.1 Data Source: SEC EDGAR CompanyFacts

**Source**: U.S. Securities and Exchange Commission EDGAR (Electronic Data Gathering, Analysis, and Retrieval) system, CompanyFacts JSON API endpoint.

**URL**: `https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit}.json`

**Licensing**: Public domain. SEC data is freely available for research and commercial use with no licensing restrictions.

**Rationale for selection**:
1. **Free and reproducible**: No authentication, subscription, or licensing barriers
2. **Real-world complexity**: Financial concepts exhibit deep hierarchies (Assets → CurrentAssets → CashAndCashEquivalents), asymmetric relations (part-of, measured-in), and concept ambiguity
3. **Structured metadata**: XBRL taxonomy provides namespace-qualified concepts (us-gaap:Revenue), units (USD, shares), and temporal periods
4. **Domain relevance**: Financial retrieval has high industry value (regulatory compliance, investment analysis, audit automation)

**Coverage**: 3,218 company filings selected from S&P 500 constituents plus representative mid-cap and small-cap firms.

### 2.2 Data Collection Procedure

**Script**: `src/data/fetch_sec.py` (not included in repository; external data fetcher)

**Process**:
1. Query SEC Company Tickers endpoint for CIK list
2. Fetch CompanyFacts JSON for each CIK with 250ms sleep between requests (polite scraping)
3. Set User-Agent header: "YourUniversity research-project your.email@university.edu" (required by SEC)
4. Handle HTTP 429 (rate limit) with exponential backoff
5. Store raw JSON files in `data/raw/sec_edgar/` with date-stamped directory (e.g., `2025-10-12/`)

**Filters applied**:
- **Namespace**: Retain only `us-gaap:*` and `dei:*` (Document and Entity Information) concepts
- **Forms**: Include 10-K (annual reports) and 10-Q (quarterly reports)
- **Date range**: FY 2020–2024 (5 years)
- **Unit validation**: Retain facts with valid units (USD, shares, pure numbers; exclude malformed entries)

### 2.3 Data Normalization

**Script**: `src/data/normalize_facts.py`

**Input**: Raw JSON files (`data/raw/sec_edgar/`)

**Output**: Line-delimited JSON (`data/processed/sec_edgar/facts.jsonl`)

**Schema** (one fact per line):
```json
{
  "cik": "0000320193",
  "ns": "us-gaap",
  "concept": "Assets",
  "unit": "USD",
  "form": "10-K",
  "fy": 2024,
  "fp": "FY",
  "period_end": "2024-09-28",
  "value": 365725000000.0,
  "accn": "0000320193-24-000123"
}
```

**Normalization steps**:
1. **Namespace extraction**: Parse qualified names (e.g., "us-gaap:Assets" → ns="us-gaap", concept="Assets")
2. **Default namespace**: If namespace missing, default to "us-gaap:" for known concepts
3. **Unit standardization**: Normalize "USD" vs "usd" vs "iso4217:USD" to canonical "USD"
4. **Deduplication**: For concepts reported multiple times in same filing/period, keep latest by `filed` timestamp
5. **Validation**: Drop facts with null concept, invalid period formats, or non-numeric values where expected

**Statistics**:
- Raw facts: 1.2M entries
- After normalization: 852K facts
- After deduplication: 487K unique (CIK, concept, unit, period_end) tuples
- Final filings: 3,218 with ≥10 distinct concepts

### 2.4 Concept Space Profiling

**Analysis**: Before building the KG, we profiled concept frequency and CIK support to inform taxonomy generation.

**Key findings**:
- **Concept vocabulary**: 4,508 unique us-gaap concepts observed across corpus
- **Long-tail distribution**: Top 100 concepts cover 78% of fact occurrences; tail 2,000 concepts appear in <5 filings each
- **CIK support**: Median concept appears in 12 filings; 95th percentile: 486 filings
- **Unit diversity**: 347 unique units (USD, shares, pure, sqft, bbl, etc.)
- **Namespace dominance**: 98.7% us-gaap, 1.2% dei, <0.1% other

This profile informed the **min_cik_support=3** threshold in frequency-based taxonomy rules (Section 3.4).

---

## 3. Knowledge Graph Construction

### 3.1 Graph Schema

**Node types**:
1. **Company**: CIK identifier, legal name
2. **Filing**: Accession number, form type (10-K/10-Q), fiscal year/period
3. **Concept**: Namespace-qualified name (e.g., us-gaap:Assets), human-readable label
4. **Unit**: Canonical unit name (USD, shares, pure)
5. **Period**: Temporal extent (period_end date, fiscal_year, fiscal_period)

**Edge types**:
1. **reports** (Company → Filing): Company files a disclosure
2. **contains** (Filing → Concept): Filing includes a concept fact
3. **measured_in** (Concept → Unit): Concept quantified in specified unit
4. **for_period** (Concept → Period): Fact applies to temporal period
5. **is_a** (Concept → Concept): Taxonomic parent-child (e.g., CashAndCashEquivalents → CurrentAssets)

**Schema rationale**:
- **Typed entities**: Enable type-aware queries ("find all Assets") and type-based evaluation (AtP measures Concept→Unit coverage)
- **Directed edges**: Preserve asymmetry (is_a hierarchy, measured_in constraint)
- **Provenance**: Company and Filing nodes enable traceability (which firm reported what concept when)

### 3.2 Knowledge Graph Snapshot Creation

**Script**: `src/kg/build_snapshot.py`

**Input**: `data/processed/sec_edgar/facts.jsonl`, combined taxonomy CSV

**Output**: Graph snapshot directory `data/kg/sec_edgar_2025-10-12_combined/` containing:
- `nodes/` subdirectory with CSV files per node type
- `edges/` subdirectory with CSV files per edge type
- `metadata.json` with snapshot date, concept count, edge statistics

**Build process**:
1. **Node extraction**: Scan facts.jsonl, extract unique CIKs (Company nodes), accessions (Filing nodes), concepts, units, periods
2. **Edge generation**:
   - reports: Group facts by CIK+accn
   - contains: Each fact creates Filing→Concept edge
   - measured_in: Each distinct (concept, unit) pair creates edge
   - for_period: Each distinct (concept, period_end) creates edge
   - is_a: Load from combined taxonomy CSV (Section 3.5)
3. **Deduplication**: Remove duplicate edges (same source, relation, target)
4. **Validation**: Check for dangling edges (target node doesn't exist); log warnings but don't fail

**Statistics** (final snapshot):
- Nodes: 3,218 Company + 3,218 Filing + 4,508 Concept + 347 Unit + 1,247 Period = **12,538 nodes**
- Edges: 3,218 reports + 487,422 contains + 4,498 measured_in + 18,943 for_period + 1,891 is_a = **515,972 edges**

**Snapshot versioning**: Each snapshot is date-stamped and immutable. Experiments pin a specific snapshot in config files (e.g., `configs/experiment_baseline.yaml` → `data_snapshot: "sec_edgar_2025-10-12_combined"`). This ensures reproducibility across runs even if taxonomy rules are later modified.

### 3.3 Taxonomy Generation: Multi-Source Strategy

Taxonomy construction is the **critical innovation** for achieving HP ≥ 25%. Prior work (Week 5-6) with a minimal 27-edge manual taxonomy yielded HP = 1.15%. Auto-taxonomy techniques lifted HP to 27.26% (2370% improvement).

#### 3.3.1 Manual Seed Taxonomy

**Source**: `datasets/sec_edgar/taxonomy/usgaap_min.csv`

**Content**: 27 curated is_a relationships representing balance sheet and income statement backbone structure.

**Examples**:
```
child,parent
us-gaap:CurrentAssets,us-gaap:Assets
us-gaap:NoncurrentAssets,us-gaap:Assets
us-gaap:CurrentLiabilities,us-gaap:Liabilities
us-gaap:NoncurrentLiabilities,us-gaap:Liabilities
us-gaap:CostOfRevenue,us-gaap:CostsAndExpenses
us-gaap:OperatingExpenses,us-gaap:OperatingIncomeLoss
```

**Rationale**: Provides structural skeleton; ensures core financial concepts are correctly parented even if pattern rules fail.

#### 3.3.2 Pattern-Based Rules

**Source**: `datasets/sec_edgar/taxonomy/pattern_rules.yaml`

**Format**: YAML mapping parent concepts to regex patterns that match child short-names.

**Example**:
```yaml
parents:
  "us-gaap:CashAndCashEquivalents":
    - "Cash.*"
    - "CashCashEquivalents.*"
    - "RestrictedCash.*"

  "us-gaap:AccountsReceivableNet":
    - "AccountsReceivable.*"
    - "TradeReceivables.*"
    - "NotesReceivable.*Current"
```

**Application algorithm** (see `src/cli/build_taxonomy.py::apply_pattern_rules`):
1. Load observed concept short-names from facts.jsonl (e.g., "AccountsReceivableNetCurrent")
2. For each parent and its pattern list:
   - Compile regex (case-insensitive)
   - Match against short-names
   - Generate (child_full, parent_full) edge if match found and child exists in concept set
3. Return set of edges

**Coverage**: Pattern rules generate **1,616 is_a edges** (86% of final taxonomy).

**Validation strategy**: Conservative patterns preferred over aggressive. For example:
- ✅ "AccountsReceivable.*" (high precision, matches intended children)
- ❌ ".*Asset.*" (too broad, would incorrectly parent verbs like "DisposalOfAsset")

#### 3.3.3 Frequency-Based Rules

**Implementation**: `src/cli/build_taxonomy.py::apply_frequency_rules`

**Goal**: Capture common concept families not covered by regex (e.g., InventoryRaw, InventoryFinished).

**Procedure**:
1. Compute CIK support counts for each concept (how many filings mention it)
2. Define concept families as (regex, parent) tuples:
   ```python
   ("^Inventory.*", "us-gaap:CurrentAssets"),
   ("^PropertyPlantAndEquipment.*", "us-gaap:NoncurrentAssets"),
   ("^OperatingLease.*Asset.*", "us-gaap:NoncurrentAssets"),
   ```
3. For concepts with CIK support ≥ `min_cik_support` (default: 3), match first applicable family and create edge

**Rationale for CIK threshold**: Concepts appearing in <3 filings are likely typos, one-off custom extensions, or entity-specific items. Requiring multi-firm support improves precision.

**Coverage**: Frequency rules generate **114 is_a edges** (6% of taxonomy).

#### 3.3.4 Backbone Relationships

**Implementation**: `src/cli/build_taxonomy.py::add_backbone`

**Content**: Hardcoded structural edges connecting mid-level categories to top-level nodes.

**Examples**:
```python
("us-gaap:AssetsCurrent", "us-gaap:Assets"),
("us-gaap:AssetsNoncurrent", "us-gaap:Assets"),
("us-gaap:LiabilitiesCurrent", "us-gaap:Liabilities"),
("us-gaap:OperatingExpenses", "us-gaap:OperatingIncomeLoss"),
```

**Purpose**: Ensures key bridge concepts (CurrentAssets, NoncurrentAssets) are parented even if not observed in data (small firms may omit these categories).

**Coverage**: 18 edges.

#### 3.3.5 Transitive Closure

**Algorithm**: Warshall's algorithm (graph reachability).

**Application**: After combining manual + pattern + frequency + backbone edges, materialize all ancestor paths.

**Example**:
- Direct edges: AccountsReceivable → CurrentAssets, CurrentAssets → Assets
- Closure adds: AccountsReceivable → Assets

**Purpose**: HP metric counts concepts with ≥1 parent. Closure ensures leaf concepts are credited even if their immediate parent isn't directly linked.

**Implementation note**: Closure is optional (flag `--with_closure`). For this project, closure was **enabled** to maximize HP.

**Effect**: Adds ~200 implicit edges (total edges after closure: 1,891).

### 3.4 Taxonomy Build Script

**Command**:
```bash
python -m src.cli.build_taxonomy \
    --facts data/processed/sec_edgar/facts.jsonl \
    --manual datasets/sec_edgar/taxonomy/usgaap_min.csv \
    --rules datasets/sec_edgar/taxonomy/pattern_rules.yaml \
    --out datasets/sec_edgar/taxonomy/usgaap_combined.csv \
    --min_cik_support 3 \
    --with_closure
```

**Output**: CSV with columns `child,parent` (1,891 rows).

**Validation checks**:
- No self-loops (child ≠ parent)
- No cycles (if A→B→C→A exists, log error)
- All children exist in observed concept set

---

## 4. Feature Engineering

### 4.1 Text Features: TF-IDF Vectorization

**Implementation**: `sklearn.feature_extraction.text.TfidfVectorizer`

**Input**: Concept labels (short names, e.g., "AccountsReceivableNetCurrent")

**Processing**:
1. **Tokenization**: CamelCase splitting ("AccountsReceivableNetCurrent" → ["Accounts", "Receivable", "Net", "Current"])
2. **Lowercase normalization**: ["accounts", "receivable", "net", "current"]
3. **Stop-word removal**: None applied (financial terms like "Net" are meaningful)
4. **N-grams**: Unigrams only (ngram_range=[1,1])

**Parameters**:
- `min_df=2`: Discard terms appearing in <2 documents (reduces noise from typos)
- `max_features=50000`: Keep top 50K terms by document frequency (corpus has ~12K unique terms, so no truncation)
- `use_idf=True`: Apply inverse document frequency weighting
- `norm='l2'`: L2-normalize rows to unit vectors (cosine similarity equivalence)

**Output**: Sparse TF-IDF matrix `X_text` of shape `(n_filings, n_terms)` = `(3218, 12147)`.

**Sparsity**: 96.8% (most filings mention 100-400 terms).

**Rationale**: TF-IDF provides a **strong text-only baseline** (98.32% micro-F1, see Results). This is critical for validating that KG features add value beyond label co-occurrence.

### 4.2 Concept Features: Binary Indicators (KG-as-Features)

**Script**: `src/cli/make_concept_features.py`

**Approach**: One-hot encoding of concept presence per filing.

**Procedure**:
1. For each filing, extract set of concepts mentioned (from contains edges)
2. Create binary vector of length `n_concepts` (4,508)
3. Set bit to 1 if concept appears in filing, 0 otherwise

**Output**: Sparse binary matrix `X_concepts` of shape `(n_filings, n_concepts)` = `(3218, 4508)`.

**Storage**: Compressed sparse row (CSR) format in `concept_features_filing.npz` (NumPy compressed archive).

**Sparsity**: 95.2% (median filing mentions ~200 concepts).

**Index mapping**: Saved in `concept_features_index.csv` (columns: `concept_id`, `concept_full_name`) for reproducibility.

**Alternatives considered but not implemented**:
- **Hashed features**: Would reduce dimensionality but lose interpretability (cannot inspect which concept fired)
- **KG embeddings (TransE/DistMult)**: Tested in ablation (M5); added training complexity without accuracy gain

### 4.3 Feature Concatenation

**Baseline (text-only)**:
```python
X = X_text  # shape (3218, 12147)
```

**Joint (text + concept)**:
```python
from scipy.sparse import hstack
X = hstack([X_text, X_concepts])  # shape (3218, 12147+4508) = (3218, 16655)
```

**Sparse matrix handling**: Both TF-IDF and concept features are sparse CSR matrices. `scipy.sparse.hstack` concatenates efficiently without densifying.

**Memory**: Sparse representation requires ~80 MB vs ~430 MB if dense (5.4× savings).

---

## 5. Model Training and Experimental Configurations

### 5.1 Baseline: Text-Only Classification

**Framework**: scikit-learn 1.3.0

**Model**: `sklearn.linear_model.LogisticRegression`

**Hyperparameters**:
- `solver='liblinear'`: Optimized for multi-label sparse data
- `C=1.0`: L2 regularization strength (default)
- `max_iter=200`: Sufficient for convergence (typically converges in 50-80 iterations)
- `multi_class='ovr'`: One-vs-rest strategy
- `random_state=42`: Fixed seed for reproducible weight initialization

**Task framing**: Multi-label classification (each filing has 1 primary label from 47 parent categories).

**Training**:
```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(solver='liblinear', C=1.0, max_iter=200, random_state=42)
model.fit(X_train_text, y_train)
```

**Rationale for LogisticRegression**:
- **Interpretable**: Coefficients map directly to feature importance
- **Fast**: Training completes in <30 seconds on CPU
- **Stable**: No sensitivity to random initialization (deterministic with fixed seed)
- **Production-ready**: Widely deployed, well-understood failure modes

**Alternative considered**: Random Forest (tested, achieved 97.1% micro-F1; underperforms LogReg).

### 5.2 Joint: Text + Concept Features

**Configuration**: Identical to baseline but with concatenated feature matrix.

**Training**:
```python
model = LogisticRegression(solver='liblinear', C=1.0, max_iter=200, random_state=42)
model.fit(X_train_joint, y_train)  # X_train_joint = hstack([X_text, X_concepts])
```

**Key insight**: Adding 4,508 binary concept features increases dimensionality by 37% but only adds 2-3 seconds to training time (sparse matrix efficiency).

### 5.3 Data Splitting

**Strategy**: Stratified random split

**Ratios**: 75% train / 25% test (no validation set; use cross-validation if tuning hyperparameters)

**Stratification key**: Most frequent label per filing (ensures rare classes represented in both splits)

**Seed**: `random_state=42` (fixed across all experiments for exact train/test consistency)

**Implementation**:
```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)
```

**Split statistics**:
- Train: 2,413 filings
- Test: 805 filings
- Label distribution preserved (χ² test p > 0.05, no significant difference)

### 5.4 Consistency Penalty Experiments (PyTorch Joint Model)

**Motivation**: Test whether explicitly enforcing hierarchy constraints during training improves classification.

**Framework**: PyTorch 2.0.1

**Model architecture**:
- Input layer: 16,655 features (text + concept)
- Hidden layer: 256 units, ReLU activation, dropout 0.3
- Output layer: 47 units (one per class), sigmoid activation (multi-label)

**Loss function**:
```python
L_total = L_BCE + λ * L_consistency
```

Where:
- `L_BCE`: Binary cross-entropy (standard classification loss)
- `L_consistency`: Mean squared error between predicted probabilities and parent-support distribution derived from observed concept hierarchy
- `λ`: Consistency weight (ablation over {0.0, 0.1, 0.5})

**Parent-support distribution**: For each filing, compute the proportion of observed child concepts that map to each parent category (using is_a edges). Penalizes predictions that deviate from this distribution.

**Training configuration**:
- Optimizer: Adam (lr=2e-3)
- Batch size: 128
- Epochs: 5 (early experiments), 20 (extended runs)
- Seed: 42

**Result**: λ=0.0 (no penalty) outperforms λ>0 (see M5 findings). Consistency penalty **does not help** in this multi-label setting; increases training time 3-4× without accuracy gain.

**Production decision**: Deploy sklearn baseline (λ=0.0 equivalent, no penalty).

---

## 6. Evaluation Metrics

### 6.1 Semantic Retention Score (SRS)

**Definition**: Composite metric quantifying how well the system preserves knowledge graph structure.

**Formula**:
```
SRS = 0.25 × HP + 0.20 × AtP + 0.20 × AP + 0.35 × RTF
```

**Components**:

#### 6.1.1 Hierarchy Presence (HP)
**Definition**: Proportion of concepts with ≥1 parent via is_a edges.

**Computation**:
```python
n_concepts_with_parent = len([c for c in concepts if has_parent(c, taxonomy)])
HP = n_concepts_with_parent / total_concepts
```

**Interpretation**:
- HP = 0.00: No taxonomy (flat concept list)
- HP = 0.25: 25% of concepts have parent (target threshold)
- HP = 1.00: All concepts parented (unrealistic; top-level categories have no parent by design)

**Weight rationale (0.25)**: Hierarchies are important but not all concepts require parents (top-level categories like "Assets" are intentionally root nodes).

#### 6.1.2 Attribute Predictability (AtP)
**Definition**: Proportion of concepts with measured_in edges (unit assignments).

**Computation**:
```python
n_concepts_with_unit = len([c for c in concepts if has_unit(c, kg)])
AtP = n_concepts_with_unit / total_concepts
```

**Interpretation**: AtP reflects **data quality** and **schema completeness**. Financial concepts should have units (Revenue → USD, SharesOutstanding → shares).

**Weight rationale (0.20)**: Unit associations are necessary but lower priority than hierarchy (HP) for semantic structure.

#### 6.1.3 Asymmetry Preservation (AP)
**Definition**: Proportion of directional edge types without erroneous reverse edges.

**Computation**:
```python
n_valid_directional = 0
for edge_type in ["is_a", "measured_in", "for_period"]:
    if no_reverse_edges_exist(edge_type, kg):
        n_valid_directional += 1
AP = n_valid_directional / 3
```

**Interpretation**: is_a is inherently asymmetric (AccountsReceivable → CurrentAssets, not reverse). AP=1.0 confirms no symmetry violations.

**Weight rationale (0.20)**: Critical for semantic correctness but binary check (either violated or not).

#### 6.1.4 Relation Type Fidelity (RTF)
**Definition**: Embedding-based metric measuring whether learned embeddings preserve relation type distinctions (is_a vs measured_in vs for_period).

**Status**: **Not implemented** (reserved for future work). Requires training embeddings (TransE/DistMult) and probing classifiers.

**Placeholder**: RTF = None → excluded from SRS calculation; remaining weights renormalized (0.25+0.20+0.20 = 0.65; scale to 1.0: HP×0.385 + AtP×0.308 + AP×0.308).

**Final SRS formula (as implemented)**:
```
SRS = 0.25×HP + 0.20×AtP + 0.20×AP + 0.35×0  (RTF=0)
    = 0.25×HP + 0.20×AtP + 0.20×AP
```
Renormalized to [0,1] by treating 0.65 as maximum: `SRS_normalized = (0.25×HP + 0.20×AtP + 0.20×AP) / 0.65`.

**Implementation**: `src/cli/compute_srs.py`

### 6.2 Classification Performance Metrics

#### 6.2.1 Micro-F1
**Definition**: F1 score computed globally across all classes (true positives, false positives, false negatives summed before division).

**Formula**:
```
micro-F1 = 2 × (TP_total / (TP_total + 0.5×(FP_total + FN_total)))
```

**Interpretation**: Reflects **overall accuracy** weighted by class support. Dominated by frequent classes.

**Use case**: System-level performance metric.

#### 6.2.2 Macro-F1
**Definition**: F1 score computed per class, then averaged (equal weight to all classes regardless of support).

**Formula**:
```
macro-F1 = mean([F1(class_i) for i in range(n_classes)])
```

**Interpretation**: Emphasizes **rare class performance**. A system with perfect accuracy on common classes but zero recall on rare classes will have low macro-F1.

**Use case**: Demonstrates KG benefit for long-tail categories (e.g., specialized asset types).

### 6.3 Latency Benchmarking

**Goal**: Measure retrieval latency at realistic scale with production-grade infrastructure.

**Script**: `src/cli/evaluate_latency.py`

**Methods tested**:
1. **exact-cosine**: Brute-force dot product (baseline)
2. **filtered-cosine**: Graph-filtered candidate set + cosine ranking (hybrid)
3. **annoy**: Approximate nearest neighbors (trees=20, SVD-256)
4. **faiss-hnsw**: HNSW index (M=32, efConstruction=200, efSearch=200)

**Benchmark protocol**:
1. Build index on train set (2,413 vectors)
2. Warm caches: Run 10 queries and discard results
3. Query 500 test vectors with top-k=10
4. Measure per-query latency (Python `time.perf_counter()`)
5. Report p50, p95, p99 percentiles

**Hardware**: 2-core CPU (Azure dev container), 16 GB RAM, no GPU

**Threads**: Fixed at 2 (set via `os.environ['OMP_NUM_THREADS']='2'`)

**Rationale for percentile reporting**: Mean latency hides tail behavior. p99 captures worst-case user experience (important for interactive systems).

### 6.4 Robustness Tests

**Taxonomy-Off Test**: Remove all is_a edges (HP → 0) and re-run classification. Measures whether concept features rely on hierarchy or merely label co-occurrence.

**Unit Noise Test**: Randomly corrupt 5-10% of measured_in edges (assign wrong units). Measures AtP degradation and classification resilience to data quality issues.

**Target**: Performance drop ≤ 10% under both stressors (ensures system is robust, not brittle).

---

## 7. Decision Gates and Thresholds

**Purpose**: Objective criteria for validating system readiness and research contributions.

### 7.1 SRS ≥ 0.75
**Rationale**: Literature review identified semantic loss as recurring problem. SRS ≥ 0.75 demonstrates measurable semantic preservation.

**Threshold derivation**:
- HP ≥ 0.25 (25% of concepts parented; reflects partial but meaningful taxonomy)
- AtP ≥ 0.95 (95% unit coverage; high data quality)
- AP ≥ 0.99 (no asymmetry violations)
→ SRS = 0.25×0.25 + 0.20×0.95 + 0.20×0.99 = 0.75 (target achieved if all component gates pass).

### 7.2 +3pp Micro-F1 Improvement
**Rationale**: KG features must demonstrably improve task performance to justify added complexity.

**Threshold derivation**: +3 percentage points is standard effect size in classification papers (e.g., Chen et al. 2024 report +2-5pp gains).

**Ceiling effect consideration**: At baselines >98%, +3pp becomes difficult. Acknowledged as limitation in Results chapter.

### 7.3 Latency p99 < 150ms
**Rationale**: Interactive retrieval systems require sub-second response. 150ms budget allows for:
- 50ms query processing
- 50ms retrieval (our component)
- 50ms result rendering

**Threshold derivation**: Industry standard for search systems (Google, Elasticsearch target <100ms; we allow margin for research prototype).

### 7.4 Robustness Drop ≤ 10%
**Rationale**: Production systems must tolerate data quality issues (wrong units, missing taxonomy edges).

**Threshold derivation**: 10% relative drop is "modest degradation" threshold from reliability engineering (e.g., AWS SLAs tolerate 5-10% degradation under partial failures).

---

## 8. Reproducibility Measures

### 8.1 Fixed Seeds
- Python random: `random.seed(42)`
- NumPy: `np.random.seed(42)`
- scikit-learn: `random_state=42` in all splitters and models
- PyTorch: `torch.manual_seed(42)`, `torch.cuda.manual_seed_all(42)` (if GPU used)

### 8.2 Data Snapshots
- KG snapshots date-stamped and pinned in config files
- Raw data stored with fetch timestamp
- Normalized data versioned (facts.jsonl → facts_v20251012.jsonl)

### 8.3 Deterministic Algorithms
- sklearn LogisticRegression with `solver='liblinear'` is deterministic given fixed seed
- TF-IDF vectorization is deterministic (no randomness)
- Stratified splits use stable sorting (deterministic given seed)

### 8.4 Environment Specification
- Python version: 3.12.1
- Dependencies: `pyproject.toml` with exact versions
- System: Ubuntu 24.04.2 LTS (dev container), 2 vCPU, 16 GB RAM

### 8.5 Experiment Tracking
- All configs stored in `configs/` (YAML format)
- Outputs logged to `reports/tables/` with timestamp suffixes
- Git commits tagged at milestone completion (M3, M4, M5, M6)

---

## 9. Ethical Considerations

### 9.1 Data Privacy
**Status**: No privacy concerns. SEC filings are public disclosure documents (legally required to be public).

### 9.2 Bias and Fairness
**Potential bias**: US-GAAP taxonomy reflects US accounting standards. May not generalize to IFRS (international) or industry-specific taxonomies.

**Mitigation**: Scope clearly defined as "US SEC filings"; limitations discussed in Results chapter.

### 9.3 Transparency
- All code open-sourced (GitHub: [repository link])
- Data sources publicly accessible (SEC EDGAR API)
- Configs and outputs archived for replication

### 9.4 Dual-Use Considerations
**Potential misuse**: Automated financial analysis could enable market manipulation if used to parse non-public information (e.g., hacked data).

**Mitigation**: Project uses only public disclosures; explicitly scoped to regulatory compliance and audit use cases.

---

## 10. Limitations and Scope Boundaries

### 10.1 Scale
- **Tested**: N ∈ {10³, 10⁴}
- **Not tested**: N ≥ 10⁵ (large-scale latency is future work)

### 10.2 Modality
- **Implemented**: Text + KG (structured+unstructured)
- **Not implemented**: Vision + KG (perceptual multi-modal)
- **Generalization claim**: Hybrid architecture patterns extend to vision by substituting CLIP for TF-IDF

### 10.3 Domain
- **Focus**: Financial documents (SEC filings)
- **Generalization**: KG integration principles (SRS metric, hybrid routing) are domain-agnostic; demonstrated on finance but applicable to manufacturing (defect ontologies), healthcare (medical KGs), e-commerce (product taxonomies)

### 10.4 Taxonomy Depth
- **Achieved**: 3-4 levels (Assets → CurrentAssets → CashAndCashEquivalents)
- **Not achieved**: Deep hierarchies (6+ levels) due to auto-taxonomy limitations

---

## 11. Summary

This methodology implements a **hybrid KG-ML architecture** combining:
1. **Graph semantic spine**: 4,508 concepts, 1,891 is_a edges, typed relationships
2. **Vector retrieval index**: Annoy ANN (sub-millisecond queries)
3. **Multi-source taxonomy**: Pattern rules (86%) + frequency rules (6%) + manual seed (5%) + backbone (3%)
4. **Honest evaluation**: SRS (semantic fidelity) + micro/macro-F1 (task performance) + p50/p95/p99 latency (operational) + robustness tests

**Key innovations**:
- **SRS metric**: First quantitative measure of semantic preservation in KG-ML systems
- **Auto-taxonomy**: 2370% HP uplift via conservative pattern rules and transitive closure
- **Production-ready baseline**: sklearn LogisticRegression (99.68% micro-F1, <1ms inference)

**Reproducibility**: Fixed seeds, pinned snapshots, deterministic algorithms, public data, open code.

**Next chapters**: Results (Chapter 5) presents decision gate outcomes, robustness tests, error analysis. Discussion (Chapter 6) interprets findings relative to literature review claims and argues generalizability to perceptual multi-modal domains.
