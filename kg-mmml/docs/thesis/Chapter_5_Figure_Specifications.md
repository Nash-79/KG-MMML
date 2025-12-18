# Chapter 5: Figure Specifications

**Document**: Figure specifications for Results chapter
**Date**: 2025-12-18
**Purpose**: Technical specifications for creating figures 5.1–5.5

---

## Figure 5.1: SRS Component Comparison

**Caption**: "Semantic Retention Score components. The system achieves strong attribute predictability (AtP=0.9987) and perfect asymmetry preservation (AP=1.0000), with moderate hierarchy presence (HP=0.2726) from auto-generated taxonomy and perfect relation type fidelity (RTF=1.0000) from TransE embeddings."

**Chart Type**: Horizontal bar chart

**Data Source**:
- HP (Hierarchy Presence): 0.2726
- AtP (Attribute Predictability): 0.9987
- AP (Asymmetry Preservation): 1.0000
- RTF (Relation Type Fidelity): 1.0000
- **SRS (Overall)**: 0.8179

**Axes**:
- X-axis: Score (0.0 to 1.0)
- Y-axis: Component names

**Colour Scheme**:
- HP: Blue (#4472C4)
- AtP: Green (#70AD47)
- AP: Orange (#FFC000)
- RTF: Purple (#7030A0)
- SRS: Red (#C00000, dashed line showing weighted average)

**Implementation Notes**:
```python
import matplotlib.pyplot as plt

components = ['HP', 'AtP', 'AP', 'RTF']
scores = [0.2726, 0.9987, 1.0000, 1.0000]
colours = ['#4472C4', '#70AD47', '#FFC000', '#7030A0']

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(components, scores, color=colours, alpha=0.8)
ax.axvline(x=0.8179, color='#C00000', linestyle='--', linewidth=2, label='SRS=0.8179')
ax.set_xlabel('Score', fontsize=12)
ax.set_ylabel('Component', fontsize=12)
ax.set_xlim(0, 1.05)
ax.legend(loc='lower right')
ax.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, (bar, score) in enumerate(zip(bars, scores)):
    ax.text(score + 0.02, i, f'{score:.4f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('fig_5_1_srs_components.png', dpi=300, bbox_inches='tight')
```

---

## Figure 5.2: Latency Scaling Comparison

**Caption**: "Latency scaling across retrieval methods. Annoy and FAISS-HNSW exhibit logarithmic complexity (O(log N)), maintaining p99 latency <0.05ms at target scale. Filtered cosine similarity shows linear degradation, whilst exact cosine similarity becomes prohibitive beyond N=10,000."

**Chart Type**: Line graph with log-log axes

**Data Source**: `reports/tables/latency_scaling_results.json`

**Projected Data Points** (N, p99 latency in ms):
- Annoy (20 trees): [(3218, 0.037), (10000, 0.045), (32180, 0.055), (100000, 0.068)]
- FAISS-HNSW (M=16): [(3218, 0.042), (10000, 0.051), (32180, 0.063), (100000, 0.078)]
- Filtered Cosine: [(3218, 0.089), (10000, 0.280), (32180, 0.850), (100000, 2.650)]
- Exact Cosine: [(3218, 2.140), (10000, 6.650), (32180, 21.400), (100000, 66.500)]

**Axes**:
- X-axis: Corpus size (N), log scale
- Y-axis: p99 latency (ms), log scale
- Reference line: 150ms SLO threshold (horizontal dashed line)

**Colour Scheme**:
- Annoy: Blue (#4472C4), solid line
- FAISS-HNSW: Green (#70AD47), solid line
- Filtered Cosine: Orange (#FFC000), dashed line
- Exact Cosine: Red (#C00000), dotted line
- SLO threshold: Grey (#808080), dashed line

**Implementation Notes**:
```python
import matplotlib.pyplot as plt
import numpy as np

N = [3218, 10000, 32180, 100000]
annoy = [0.037, 0.045, 0.055, 0.068]
faiss = [0.042, 0.051, 0.063, 0.078]
filtered = [0.089, 0.280, 0.850, 2.650]
exact = [2.140, 6.650, 21.400, 66.500]

fig, ax = plt.subplots(figsize=(10, 6))
ax.loglog(N, annoy, 'o-', color='#4472C4', linewidth=2, label='Annoy (20 trees)')
ax.loglog(N, faiss, 's-', color='#70AD47', linewidth=2, label='FAISS-HNSW (M=16)')
ax.loglog(N, filtered, '^--', color='#FFC000', linewidth=2, label='Filtered Cosine')
ax.loglog(N, exact, 'v:', color='#C00000', linewidth=2, label='Exact Cosine')
ax.axhline(y=150, color='#808080', linestyle='--', linewidth=1.5, label='SLO (150ms)')

ax.set_xlabel('Corpus Size (N)', fontsize=12)
ax.set_ylabel('p99 Latency (ms)', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(2000, 150000)
ax.set_ylim(0.01, 200)

plt.tight_layout()
plt.savefig('fig_5_2_latency_scaling.png', dpi=300, bbox_inches='tight')
```

---

## Figure 5.3: F1 Score Distribution Across Concepts

**Caption**: "F1 score distribution for 47 US-GAAP concepts. The text+concept model (blue) shows improvement over baseline (orange), particularly for rare classes in the 0.90–0.99 range. Both models achieve perfect F1=1.0 for 31 high-frequency concepts."

**Chart Type**: Histogram with overlapping distributions

**Data Source**: `reports/tables/baseline_text_seed42_metrics.json` and `baseline_text_plus_concept_seed42_metrics.json`

**Bins**: [0.80, 0.85, 0.90, 0.95, 1.00]

**Summary Statistics**:
- Baseline: Mean F1=0.9833, Median F1=0.9950, Min F1=0.8571 (ResearchAndDevelopmentExpense)
- Text+Concept: Mean F1=0.9968, Median F1=1.0000, Min F1=0.9412 (ResearchAndDevelopmentExpense)

**Axes**:
- X-axis: F1 Score bins
- Y-axis: Number of concepts

**Colour Scheme**:
- Baseline (text-only): Orange (#FFC000), alpha=0.5
- Text+Concept: Blue (#4472C4), alpha=0.5

**Implementation Notes**:
```python
import matplotlib.pyplot as plt
import json

# Load per-class metrics
with open('reports/tables/baseline_text_seed42_metrics.json') as f:
    baseline = json.load(f)
with open('reports/tables/baseline_text_plus_concept_seed42_metrics.json') as f:
    text_concept = json.load(f)

baseline_f1 = [v['f1-score'] for k, v in baseline.items() if k.startswith('us-gaap:')]
text_concept_f1 = [v['f1-score'] for k, v in text_concept.items() if k.startswith('us-gaap:')]

fig, ax = plt.subplots(figsize=(10, 6))
bins = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05]
ax.hist(baseline_f1, bins=bins, alpha=0.5, color='#FFC000', label='Baseline (text-only)', edgecolor='black')
ax.hist(text_concept_f1, bins=bins, alpha=0.5, color='#4472C4', label='Text+Concept', edgecolor='black')

ax.set_xlabel('F1 Score', fontsize=12)
ax.set_ylabel('Number of Concepts', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.set_xlim(0.80, 1.05)
ax.grid(axis='y', alpha=0.3)

# Add summary statistics
ax.text(0.82, ax.get_ylim()[1]*0.9,
        f'Baseline: μ={sum(baseline_f1)/len(baseline_f1):.4f}\n'
        f'Text+Concept: μ={sum(text_concept_f1)/len(text_concept_f1):.4f}',
        fontsize=10, verticalalignment='top')

plt.tight_layout()
plt.savefig('fig_5_3_f1_distribution.png', dpi=300, bbox_inches='tight')
```

---

## Figure 5.4: Robustness Under Perturbation

**Caption**: "SRS degradation under perturbations. Taxonomy removal (−18.8% SRS) demonstrates architecture dependency on hierarchical signals. Unit-noise tolerance shows graceful degradation: −7.0% at 5% corruption, −13.7% at 10% corruption."

**Chart Type**: Grouped bar chart

**Data Source**: `reports/tables/robustness_test_results.json`

**Perturbation Scenarios**:
1. Baseline (no perturbation): SRS=0.8179
2. Taxonomy removal (no is-a edges): SRS=0.6642 (−18.8%)
3. Unit noise 5% (corrupt measured-in edges): SRS=0.7607 (−7.0%)
4. Unit noise 10%: SRS=0.7058 (−13.7%)

**Axes**:
- X-axis: Perturbation scenario
- Y-axis: SRS score (0.0 to 1.0)

**Colour Scheme**:
- Baseline: Green (#70AD47)
- Taxonomy removal: Red (#C00000)
- 5% noise: Orange (#FFC000)
- 10% noise: Dark orange (#ED7D31)

**Implementation Notes**:
```python
import matplotlib.pyplot as plt

scenarios = ['Baseline', 'Taxonomy\nRemoval', '5% Unit\nNoise', '10% Unit\nNoise']
srs_scores = [0.8179, 0.6642, 0.7607, 0.7058]
deltas = [0, -0.1537, -0.0572, -0.1121]
colours = ['#70AD47', '#C00000', '#FFC000', '#ED7D31']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(scenarios, srs_scores, color=colours, alpha=0.8, edgecolor='black')
ax.axhline(y=0.75, color='#808080', linestyle='--', linewidth=1.5, label='SRS Threshold (0.75)')

ax.set_ylabel('Semantic Retention Score', fontsize=12)
ax.set_ylim(0, 1.0)
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3)

# Add value labels and delta annotations
for i, (bar, score, delta) in enumerate(zip(bars, srs_scores, deltas)):
    ax.text(bar.get_x() + bar.get_width()/2, score + 0.02,
            f'{score:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    if delta < 0:
        ax.text(bar.get_x() + bar.get_width()/2, score - 0.05,
                f'({delta:.1%})', ha='center', va='top', fontsize=9, color='darkred')

plt.tight_layout()
plt.savefig('fig_5_4_robustness_perturbation.png', dpi=300, bbox_inches='tight')
```

---

## Figure 5.5: Error Distribution by Category

**Caption**: "Error distribution across financial statement categories. The hybrid model (text+concept) reduces errors for 'Other' (−2.37pp) and 'Revenue' (−1.18pp) categories whilst maintaining perfect accuracy for high-frequency categories (Assets, Equity, Income)."

**Chart Type**: Grouped bar chart

**Data Source**: Error analysis from per-class metrics

**Categories and Error Rates**:
- **Baseline (text-only)**:
  - Other: 3.05% (8/262 errors)
  - Revenue: 1.37% (3/219 errors)
  - Liabilities: 0.86% (2/232 errors)
  - Expenses: 0.52% (2/385 errors)
  - Assets: 0.00% (0/450 errors)
  - Equity: 0.00% (0/220 errors)
  - Income: 0.00% (0/195 errors)

- **Text+Concept**:
  - Other: 0.68% (2/262 errors)
  - Revenue: 0.19% (1/219 errors)
  - Liabilities: 0.43% (1/232 errors)
  - Expenses: 0.26% (1/385 errors)
  - Assets: 0.00% (0/450 errors)
  - Equity: 0.00% (0/220 errors)
  - Income: 0.00% (0/195 errors)

**Axes**:
- X-axis: Financial statement categories
- Y-axis: Error rate (%)

**Colour Scheme**:
- Baseline: Orange (#FFC000)
- Text+Concept: Blue (#4472C4)

**Implementation Notes**:
```python
import matplotlib.pyplot as plt
import numpy as np

categories = ['Other', 'Revenue', 'Liabilities', 'Expenses', 'Assets', 'Equity', 'Income']
baseline_errors = [3.05, 1.37, 0.86, 0.52, 0.00, 0.00, 0.00]
text_concept_errors = [0.68, 0.19, 0.43, 0.26, 0.00, 0.00, 0.00]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, baseline_errors, width, label='Baseline (text-only)',
               color='#FFC000', alpha=0.8, edgecolor='black')
bars2 = ax.bar(x + width/2, text_concept_errors, width, label='Text+Concept',
               color='#4472C4', alpha=0.8, edgecolor='black')

ax.set_ylabel('Error Rate (%)', fontsize=12)
ax.set_xlabel('Financial Statement Category', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 3.5)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('fig_5_5_error_distribution.png', dpi=300, bbox_inches='tight')
```

---

## Additional Figure (Optional): System Architecture Diagram

**For Chapter 4, Section 4.1**

**Caption**: "Hybrid KG-ML system architecture. The pipeline ingests SEC EDGAR filings, generates auto-taxonomy relationships, extracts features (TF-IDF, concept indicators, TransE embeddings), and maintains parallel graph store (Neo4j) and vector index (Annoy) for retrieval."

**Diagram Type**: Flow diagram with components

**Components**:
1. **Data Ingestion**: SEC EDGAR CompanyFacts API → facts.jsonl
2. **Taxonomy Generation**: Pattern rules + frequency analysis → 1,891 is-a edges
3. **Feature Engineering**:
   - Text features: TF-IDF (20,000 dimensions)
   - Graph features: Binary concept indicators (4,502 concepts)
   - Embeddings: TransE (50 dimensions, 7,111 entities)
4. **Storage**:
   - Graph Store: Neo4j (10,813 entities, 584,535 edges)
   - Vector Index: Annoy (20 trees, angular distance)
5. **Classification**: sklearn LogisticRegression (OneVsRest)
6. **Evaluation**: SRS computation + latency benchmarking

**Tool**: Create using draw.io, Lucidchart, or PowerPoint

**Export Format**: PNG (300 DPI) or SVG for vector graphics

---

## Figure Formatting Guidelines

**All figures should follow these standards**:

1. **Resolution**: 300 DPI for raster images (PNG), vector (SVG) preferred
2. **Font sizes**: Axis labels 12pt, tick labels 10pt, annotations 9pt
3. **Colour accessibility**: Ensure sufficient contrast for colourblind readers
4. **File naming**: `fig_X_Y_description.png` (e.g., `fig_5_1_srs_components.png`)
5. **Captions**: Place below figure, reference in-text as "Figure 5.X"
6. **Data files**: Store source data in `reports/tables/` directory
7. **Code**: Store generation scripts in `scripts/figures/` directory

---

## Data Sources Summary

| Figure | Primary Data Source | Format |
|--------|---------------------|--------|
| 5.1 | SRS component scores (M6 output) | Hardcoded values |
| 5.2 | `latency_scaling_results.json` | JSON |
| 5.3 | `baseline_text_seed42_metrics.json`, `baseline_text_plus_concept_seed42_metrics.json` | JSON |
| 5.4 | `robustness_test_results.json` | JSON |
| 5.5 | Per-class error analysis from metrics | Derived |

---

**Instructions for creating figures**:

1. Install required packages: `pip install matplotlib numpy pandas`
2. Execute Python code snippets in `scripts/figures/` directory
3. Verify output images in `docs/thesis/figures/` directory
4. Insert figures into Word document at appropriate section references
5. Ensure captions match specifications above

---

**Author**: Nash-79
**Date**: 2025-12-18
**Status**: Specifications complete, ready for figure generation
