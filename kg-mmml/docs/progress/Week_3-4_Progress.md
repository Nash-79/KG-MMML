# Week 3-4 Progress Report

**Period:** Weeks 3-4  
**Status:** On track

---

## Summary

This period focused on establishing the data pipeline and repository structure for the knowledge graph system. We built tools to convert SEC EDGAR company filings into a structured knowledge graph and implemented the framework for measuring graph quality.

**Key achievements:**
- Built automated pipeline to fetch and process SEC EDGAR filings
- Designed knowledge graph schema (5 node types, 3 edge types)
- Created SRS computation framework
- Set up clean repository with reproducible configs
- Selected 49 companies for initial testing

---

## Data Pipeline Implementation

**Company Selection**  
Compiled 49 CIKs (Central Index Keys) for target companies, mapped 45 stock tickers to CIKs. Focused on technology sector with some diversification.

**Pipeline Scripts**  
Created 4-stage automated pipeline:

1. **Filing Selection** (`fetch_filings.py`)
   - Fetches latest 10-K and 10-Q filings per company
   - Handles 10-digit CIK padding and 404 errors gracefully
   - Output: `selected.json` with filing metadata

2. **Fast Facts Extraction** (`download_companyfacts.py`)
   - Uses SEC's CompanyFacts JSON endpoint (fast, free, reliable)
   - Avoids complex HTML/XBRL parsing
   - Downloads one JSON file per company

3. **Fact Normalization** (`companyfacts_to_facts.py`)
   - Converts nested JSON to flat structure
   - Output: `facts.jsonl` with fields: namespace, concept, unit, value, period_end, accession
   - Filters to US-GAAP concepts with numeric units

4. **KG Snapshot Builder** (`build_kg.py`)
   - Generates graph nodes and edges from normalised facts
   - Outputs: `kg_nodes.csv` and `kg_edges.csv`

**Files Generated:**
- `data/raw/sec_edgar/selected.json`
- `data/processed/sec_edgar/companyfacts/*.json`
- `data/processed/sec_edgar/facts.jsonl`
- `data/kg/sec_edgar_[DATE]/` (nodes and edges)

---

## Knowledge Graph Schema

**Node Types (5):**
- **Company** - SEC-registered entities
- **Filing** - 10-K/10-Q reports
- **Concept** - Financial concepts (e.g., us-gaap:Assets)
- **Unit** - Measurement units (USD, shares)
- **Period** - Time periods for reported values

**Edge Types (3):**
- **reports** - Company → Filing
- **measured-in** - Concept → Unit
- **for-period** - Concept → Period

**Design Principle:**  
Multi-resolution approach allows both document-level and fact-level queries.

**Documentation:**
- `datasets/sec_edgar/DATA_CHOICE.md` - Dataset selection rationale
- `datasets/sec_edgar/docs/KG_SCHEMA.md` - Graph schema specification

---

## SRS Measurement Framework

Created `compute_srs.py` to measure knowledge graph quality using 4 metrics:

**AtP (Attribute Predictability)** - Implemented  
Measures fraction of concepts with unit information. Ready to compute from Concept→Unit edges.

**HP (Hierarchy Presence)** - Planned  
Measures fraction of concepts with parent relationships. Requires taxonomy (scheduled for Week 5-6).

**AP (Asymmetry Preservation)** - Planned  
Measures correct directionality of edges. Framework ready, will activate with taxonomy.

**RTF (Relation Type Fidelity)** - Optional  
Embedding-based relationship quality. Planned for later phase.

**SRS Formula:**  
Weighted combination: AtP (20%), HP (25%), AP (20%), RTF (35%)

**Week 8 Target:** SRS ≥ 0.75

---

## Repository Structure

**Clean Organization:**
- `datasets/sec_edgar/` - Documentation and scripts
- `data/` - All generated data (git-ignored)
- `configs/` - Experiment configurations with pinned KG snapshots
- `src/cli/` - Command-line tools
- `reports/tables/` - Output metrics

**Reproducibility:**
- Fixed random seeds in all configs
- Pinned KG snapshot references in experiment configs
- Removed tracked artifacts from git

---

## Alignment to Plan

**Week 3-4 Goals:**
- Establish data acquisition pipeline
- Build initial KG snapshot
- Implement SRS computation framework
- Set up reproducible repository structure

**Week 8 Decision Gates:**

| Gate | Target | Current Status |
|------|--------|----------------|
| SRS ≥ 0.75 | ≥0.75 | Framework ready, awaiting taxonomy |
| AtP ≥ 0.95 | ≥0.95 | Can compute once KG built at scale |
| HP ≥ 0.25 | ≥0.25 | Requires taxonomy (Week 5-6) |
| AP ≥ 0.99 | ≥0.99 | Framework ready |
| +3pp micro-F1 | Text vs Text+Concept | Baseline planned for Week 5-6 |

**Status:** Foundation complete. Ready for Week 5-6 scaling and baseline measurements.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sparse taxonomy may limit HP | Could depress SRS below 0.75 | Week 5-6: Generate auto-taxonomy using pattern matching |
| API rate limiting | Slower data refresh | Use polite delays (250ms), run batch jobs off-peak |
| Small corpus per label | Unstable classification metrics | Ensure minimum docs per label, use stratified splits |

---

## Next Steps (Week 5-6)

**Goal 1: Scale and Measure**
- Scale fact extraction to larger corpus
- Build production KG snapshot
- Compute initial SRS metrics (AtP live, HP/AP with taxonomy)

**Goal 2: Baseline Classification**
- Implement text-only baseline (TF-IDF + LogisticRegression)
- Implement text+concept baseline (TF-IDF + concept features)
- Compare performance to validate KG-as-features approach

**Goal 3: Auto-Taxonomy**
- Generate conservative parent-child relationships from patterns
- Combine with small manually curated taxonomy
- Rebuild KG with taxonomy edges
- Enable HP and AP measurements

**Deliverables:**
- `baseline_text_metrics.json`
- `baseline_text_plus_concept_metrics.json`
- `baseline_vs_kge.csv`
- `srs_kge.csv` (with AtP, HP, AP scores)

---

## Lessons Learned

**What Worked Well:**
- CompanyFacts JSON endpoint provides fast, reliable data access
- Clean separation of raw/processed/kg data stages
- Fixed configs with pinned snapshots ensure reproducibility
- Modular pipeline allows easy debugging

**What to Improve:**
- Need taxonomy earlier to enable full SRS measurement
- Should plan for stratified sampling to ensure label coverage
- Could benefit from progress monitoring during long downloads
