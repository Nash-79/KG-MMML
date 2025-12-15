# M9 Error Analysis + Results Chapter Plan

**Milestone**: M9 (Week 17-18)
**Status**: In Progress
**Goals**: Error analysis on 0.32% misclassifications + Draft Results chapter

---

## Overview

M9 focuses on understanding system failures and drafting the Results & Discussion chapter for the thesis.

### Key Tasks

1. **Error Analysis** - Investigate misclassifications
2. **Visualizations** - Create figures for thesis
3. **Results Chapter** - Draft Chapter 5 structure
4. **Discussion Points** - Prepare interpretations

---

## 1. Error Analysis

### Current Performance
- **Micro-F1**: 99.68% (text+concept model)
- **Macro-F1**: 99.50%
- **Test set**: 805 documents, 26,016 labels total
- **Multi-label**: Average 32.3 labels per document

### Error Rate Calculation
- Micro-F1 = 99.68% → Error rate = 0.32%
- Misclassified labels: 26,016 × 0.0032 ≈ 83 label predictions
- Per-document errors: Variable (some documents have 0 errors, some have multiple)

### Analysis Approach

**A. Per-Label Performance Analysis**
- Identify worst-performing concepts (lowest F1 scores)
- Analyze support (sample size) correlation
- Check for semantic confusion patterns

**B. Error Pattern Analysis**
- Categorize errors by type:
  - False Positives (predicted but absent)
  - False Negatives (present but not predicted)
- Group by concept category (Assets, Liabilities, Income, etc.)

**C. Hypothesis Testing**
Why do errors occur?
1. **Low support classes**: Rare concepts have fewer training examples
2. **Semantic similarity**: Confused concepts are semantically related
3. **Taxonomy gaps**: Missing is-a edges for confused pairs
4. **Data quality**: Ambiguous or mislabelled instances

### Deliverables
- `reports/tables/m9_error_analysis.json` - Per-label error breakdown
- `reports/tables/m9_error_patterns.csv` - Categorized errors
- `docs/progress/Week_17-18_M9_Error_Analysis.md` - Detailed analysis

---

## 2. Visualizations

### Figure 1: SRS Component Comparison
**Type**: Bar chart
**Data**: HP, AtP, AP, RTF scores with/without RTF
**Purpose**: Show SRS improvement from 0.7571 → 0.8179

### Figure 2: Latency Scaling
**Type**: Line chart
**Data**: N=1000, N=3218, N=10000 (projected) for all methods
**Purpose**: Demonstrate scalability

### Figure 3: Confusion Matrix (Top 10 Concepts)
**Type**: Heatmap
**Data**: Most frequent concepts, showing prediction accuracy
**Purpose**: Visualize classification performance

### Figure 4: F1 Score Distribution
**Type**: Histogram
**Data**: Per-label F1 scores (all 47 concepts)
**Purpose**: Show overall model reliability

### Figure 5: Robustness Under Perturbation
**Type**: Bar chart
**Data**: SRS degradation under taxonomy-off, 5% noise, 10% noise
**Purpose**: Demonstrate graceful degradation

### Deliverables
- `reports/figures/srs_comparison.png`
- `reports/figures/latency_scaling.png`
- `reports/figures/confusion_matrix.png`
- `reports/figures/f1_distribution.png`
- `reports/figures/robustness_degradation.png`

---

## 3. Results Chapter Structure

### Chapter 5: Results

#### 5.1 Decision Gate Outcomes (2 pages)
- Table summarizing all gates (SRS, Latency, +3pp micro-F1)
- Pass/fail status with evidence citations
- Ceiling effect discussion for micro-F1 gate

#### 5.2 Semantic Retention Score (3 pages)
- **5.2.1 Component Metrics**
  - HP: 27.26% (taxonomy contribution)
  - AtP: 99.87% (unit coverage)
  - AP: 100% (directionality preservation)
  - RTF: 100% (embedding fidelity)
- **5.2.2 SRS Composition**
  - Formula and weighting rationale
  - Before/after RTF implementation
  - Comparison to threshold (0.75)
- **5.2.3 Interpretation**
  - What SRS=0.8179 means for semantic preservation
  - Trade-offs vs pure vector approaches

#### 5.3 Classification Performance (2 pages)
- **5.3.1 Overall Metrics**
  - Micro-F1: 99.68% (+1.36pp over baseline)
  - Macro-F1: 99.50% (+2.27pp over baseline)
  - Ceiling effect analysis
- **5.3.2 Per-Label Analysis**
  - Best performers (F1=1.0)
  - Worst performers (F1<0.98)
  - Support correlation
- **5.3.3 Error Analysis**
  - False positive/negative patterns
  - Semantic confusion examples
  - Rare class behaviour

#### 5.4 Latency Performance (2 pages)
- **5.4.1 Baseline Results** (N=3,218)
  - Annoy: 0.037ms p99 (production choice)
  - FAISS: 0.255ms p99
  - Filtered cosine: 2.429ms p99
  - Exact cosine: 5.483ms p99
- **5.4.2 Scalability Projections** (N=10,000)
  - Analytical projections
  - Logarithmic scaling validation
- **5.4.3 Two-Hop Overhead**
  - Graph expansion cost: 0.0023ms
  - Negligible impact on SLO

#### 5.5 Robustness Evaluation (2 pages)
- **5.5.1 Taxonomy Removal**
  - 18.8% SRS degradation (controlled)
  - Validates hierarchy contribution
- **5.5.2 Unit-Noise Tolerance**
  - 5% noise: 7.0% degradation (PASS)
  - 10% noise: 9.0% degradation (PASS)
  - Graceful degradation demonstrated

#### 5.6 Summary of Findings (1 page)
- Research questions answered
- Gate outcomes interpretation
- Contributions to knowledge

**Total**: ~12 pages for Results chapter

---

## 4. Timeline

### Week 17 (Days 1-3)
- [ ] Run error analysis script
- [ ] Generate all visualizations
- [ ] Draft sections 5.1-5.3

### Week 17 (Days 4-7)
- [ ] Draft sections 5.4-5.6
- [ ] Create Week 17-18 progress report
- [ ] Review and refine chapter

### Week 18
- [ ] Peer review (if available)
- [ ] Supervisor feedback integration
- [ ] Final polishing

---

## 5. Success Criteria

**Error Analysis**:
- [ ] Identified error patterns
- [ ] Hypotheses for failure modes
- [ ] Quantified error distribution

**Visualizations**:
- [ ] 5 publication-quality figures
- [ ] All figures thesis-ready (proper labels, legends)

**Results Chapter**:
- [ ] Complete draft of Chapter 5 (12 pages)
- [ ] All decision gates documented
- [ ] Error analysis integrated

---

## 6. Next Milestones

**M10** (Week 19-20): Statistical validation (5 seeds, confidence intervals)
**M11** (Week 21-22): Conclusion, Abstract, Appendices
**M12** (Week 23-24): Video demo + submission
