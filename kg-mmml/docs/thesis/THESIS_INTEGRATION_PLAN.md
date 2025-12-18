# Thesis Integration Plan

**Date**: 2025-12-18
**Status**: Complete chapters ready for final assembly

---

## Executive Summary

All major thesis chapters are complete. This document provides the integration strategy for assembling the final submission document.

**Total Word Count (excluding appendices)**: ~19,000 words
- Abstract: 280 words
- Chapter 1 (Introduction): 1,999 words
- Chapter 2 (Literature Review): ~4,500 words
- Chapter 3 (Methodology): ~5,200 words
- Chapter 4 (Implementation): ~2,800 words
- Chapter 5 (Results): ~2,000 words (with figure specifications)
- Chapter 6 (Discussion): 4,206 words
- Chapter 7 (Conclusion): 2,148 words

---

## Complete Thesis Structure

### **Single Submission Document: ONE MSc Thesis (Word/PDF)**

```
Title Page
Abstract (280 words)
Table of Contents
List of Figures
List of Tables

Chapter 1: Introduction (1,999 words)
Chapter 2: Literature Review (~4,500 words)
Chapter 3: Methodology (~5,200 words)
Chapter 4: Implementation (~2,800 words)
Chapter 5: Results (~2,000 words)
Chapter 6: Discussion (4,206 words)
Chapter 7: Conclusion (2,148 words)

References/Bibliography
Appendices (A-D)
```

---

## Chapter Status Overview

| Chapter | File Location | Status | Notes |
|---------|---------------|--------|-------|
| Abstract | `docs/thesis/Abstract.md` | ✅ Complete | 280 words, UK English |
| Ch 1: Introduction | `docs/thesis/Chapter_1_Introduction.md` | ✅ Complete | 1,999 words, includes RQ1-RQ4 |
| Ch 2: Literature Review | `docs/thesis/Chapter_2_Literature_Review.md` | ✅ Complete | Adapted from PDF, financial focus |
| Ch 3: Methodology | `docs/thesis/Chapter_3_Methodology.md` | ✅ Complete | From 01_METHODOLOGY.md, UK English |
| Ch 4: Implementation | `docs/thesis/Chapter_4_Implementation.md` | ✅ Complete | Technical details, code snippets |
| Ch 5: Results | `docs/thesis/Chapter_5_Results.md` | ✅ Complete | With figure specifications |
| Ch 5 Figures | `docs/thesis/Chapter_5_Figure_Specifications.md` | ✅ Complete | 5 figures with Python code |
| Ch 6: Discussion | `docs/thesis/Chapter_6_Discussion.md` | ✅ Complete | 4,206 words, UK English |
| Ch 7: Conclusion | `docs/thesis/Chapter_7_Conclusion.md` | ✅ Complete | 2,148 words, UK English |

---

## Missing Components (To Complete)

### 1. **Bibliography/References**

**Source Material**:
- Literature Review PDF contains 26 references
- Additional citations throughout chapters

**Action Required**:
1. Extract all references from Literature Review PDF (pages 12-14)
2. Add references for:
   - Bordes et al. (2013) - TransE
   - Sun et al. (2019) - RotatE
   - Yang et al. (2015) - DistMult
   - Trouillon et al. (2016) - ComplEx
   - Kipf and Welling (2017) - GCN
3. Format in Harvard style (UK English)
4. Create `References.md` file

**References from Literature Review PDF** (already available):
```
Baltrušaitis et al. (2019), Chen et al. (2024), Das et al. (2020),
Fey & Lenssen (2019), García-Durán & Niepert (2018), Ji et al. (2022),
Krishna et al. (2017), Liu et al. (2021), Marino et al. (2017),
Mehrabi et al. (2021), Nickel et al. (2016), Paulheim (2017),
Radford et al. (2021), Shen et al. (2021), Trivedi et al. (2017),
Veličković et al. (2018), Wang et al. (2017, 2020), Yao et al. (2019),
Zhang et al. (2019), Zhou et al. (2020), Zhu et al. (2020),
Neo4j (2025), Zhang & Wang (2024)
```

### 2. **Appendices**

#### Appendix A: Code Listings

**Content**:
- Taxonomy generation algorithm (from Chapter 4.2.3)
- SRS computation (from Chapter 3.6.1)
- Baseline classifier training (from Chapter 3.5.1)

**Files to Extract From**:
- `src/cli/build_taxonomy.py` (pattern rules, frequency rules)
- `src/cli/compute_srs.py` (SRS calculation)
- `src/cli/baseline_tfidf.py` (classifier training)

#### Appendix B: Full Metric Tables

**Content**:
- Per-label F1 scores for all 47 concepts (seed=42)
- Confusion matrices
- Latency distributions (p50/p95/p99 for all methods)

**Files to Extract From**:
- `reports/tables/baseline_text_seed42_metrics.json`
- `reports/tables/baseline_text_plus_concept_seed42_metrics.json`
- `reports/tables/latency_scaling_results.json` (if exists)

#### Appendix C: Decision Gate Documentation

**Content**:
- M3-M9 milestone reports
- Gate outcomes (SRS, latency, micro-F1)

**Files to Include**:
- `docs/EvaluationSheet_v1.md` (M5 results)
- `docs/M6_PLAN.md` (RTF implementation)
- `docs/M7_ROBUSTNESS_README.md` (robustness tests)
- `docs/M8_SCALABILITY_REPORT.md` (scalability validation)
- `docs/M9_PLAN.md` (error analysis)
- `docs/M10_SINGLE_SEED_VALIDATION_REPORT.md` (reproducibility)

#### Appendix D: Reproducibility Guide

**Content**:
- Environment setup (Python 3.12.1, dependencies)
- Data pipeline (SEC EDGAR fetch, normalisation)
- Experiment scripts (how to run baselines, compute SRS)

**Files to Reference**:
- `pyproject.toml` (dependencies)
- `README.md` (if exists)
- Key scripts in `src/cli/` and `scripts/`

### 3. **Figures**

**Status**: Specifications complete, need to generate actual images

**Five Figures Required** (from Chapter_5_Figure_Specifications.md):
1. **Figure 5.1**: SRS component comparison (bar chart)
2. **Figure 5.2**: Latency scaling comparison (log-log line graph)
3. **Figure 5.3**: F1 score distribution (histogram)
4. **Figure 5.4**: Robustness under perturbation (grouped bar chart)
5. **Figure 5.5**: Error distribution by category (grouped bar chart)

**Optional**: Figure 4.1 - System architecture diagram

**Action Required**:
1. Run Python code from `Chapter_5_Figure_Specifications.md`
2. Save as PNG (300 DPI) in `docs/thesis/figures/` directory
3. Insert into Word document at appropriate locations

---

## Assembly Instructions

### **Step 1: Create Master Document in Microsoft Word**

1. Open Microsoft Word
2. Set up document:
   - Page size: A4
   - Margins: 2.5cm (top/bottom/left/right)
   - Font: Times New Roman 12pt or Arial 11pt
   - Line spacing: 1.5 or double (check university guidelines)
   - Paragraph spacing: 6pt after

### **Step 2: Insert Front Matter**

1. **Title Page**:
   - Thesis title: "Integrating Knowledge Graphs with Multi-Modal Machine Learning: A Hybrid Architecture for Financial Concept Classification"
   - Your name
   - Degree: MSc [Your Programme]
   - University name
   - Submission date: [Month Year]

2. **Abstract** (copy from `Abstract.md`):
   - Single page
   - 280 words
   - No page number

3. **Table of Contents** (Word auto-generate):
   - Use Heading styles (Heading 1, Heading 2, Heading 3)
   - Insert → Table of Contents → Automatic

4. **List of Figures** (Word auto-generate):
   - Insert → Table of Figures

5. **List of Tables** (if applicable):
   - Insert → Table of Tables

### **Step 3: Insert Chapters**

**Copy content from each `.md` file, applying formatting**:

1. **Chapter 1: Introduction**
   - Copy from `Chapter_1_Introduction.md`
   - Apply Heading 1 for "Chapter 1: Introduction"
   - Apply Heading 2 for sections (1.1, 1.2, etc.)
   - Apply Heading 3 for subsections (1.2.1, 1.2.2, etc.)

2. **Chapter 2: Literature Review**
   - Copy from `Chapter_2_Literature_Review.md`
   - Same heading structure

3. **Chapter 3: Methodology**
   - Copy from `Chapter_3_Methodology.md`
   - Insert code snippets using "Code" style (Consolas 10pt, grey background)

4. **Chapter 4: Implementation**
   - Copy from `Chapter_4_Implementation.md`
   - Insert code snippets

5. **Chapter 5: Results**
   - Copy from `Chapter_5_Results.md`
   - **Insert figures at appropriate locations**:
     - Generate figures using Python code from `Chapter_5_Figure_Specifications.md`
     - Save as PNG (300 DPI)
     - Insert → Pictures → select figure
     - Add caption: Insert → Caption → "Figure 5.X: [caption text]"

6. **Chapter 6: Discussion**
   - Copy from `Chapter_6_Discussion.md`

7. **Chapter 7: Conclusion**
   - Copy from `Chapter_7_Conclusion.md`

### **Step 4: Insert References**

1. **Create References section**:
   - Heading 1: "References"
   - No chapter number
   - Alphabetical order by author surname

2. **Format**:
   - Harvard style (UK English)
   - Hanging indent (0.5cm)
   - Single line spacing within entries, double between entries

3. **Extract from Literature Review PDF** (pages 12-14)

### **Step 5: Insert Appendices**

1. **Appendix A: Code Listings**
   - Extract code from relevant files
   - Use "Code" style for syntax highlighting

2. **Appendix B: Full Metric Tables**
   - Convert JSON data to formatted tables
   - Use Word table styles for readability

3. **Appendix C: Decision Gate Documentation**
   - Summarise milestone reports
   - Include key tables (SRS components, latency results)

4. **Appendix D: Reproducibility Guide**
   - Environment setup instructions
   - Data pipeline steps
   - Experiment execution commands

### **Step 6: Final Formatting**

1. **Page Numbers**:
   - Front matter: Roman numerals (i, ii, iii, ...)
   - Main body: Arabic numerals (1, 2, 3, ...)
   - Insert → Page Number → Format → Number format

2. **Headers/Footers**:
   - Left header: Chapter title
   - Right header: Section title
   - Centre footer: Page number

3. **Cross-References**:
   - Update all figure/table references
   - Update all section references (e.g., "see Section 3.2.1")
   - Update table of contents
   - Insert → Update Field (or press F9)

4. **Spell Check**:
   - Language: English (United Kingdom)
   - Review → Spelling & Grammar

### **Step 7: Generate PDF**

1. **Save as PDF**:
   - File → Save As → PDF
   - Options: Include document properties, create bookmarks

2. **Verify PDF**:
   - Check all figures display correctly
   - Check page numbers
   - Check hyperlinks (table of contents, references)

---

## Quality Checklist

### **Content Completeness**
- [ ] All chapters present (1-7)
- [ ] Abstract included
- [ ] References/bibliography included
- [ ] All 4 appendices included
- [ ] All 5 figures generated and inserted

### **Formatting Consistency**
- [ ] Consistent heading styles throughout
- [ ] Consistent font (Times New Roman 12pt or Arial 11pt)
- [ ] Consistent line spacing (1.5 or double)
- [ ] Page numbers correct (Roman for front, Arabic for body)
- [ ] Table of contents up-to-date
- [ ] List of figures up-to-date

### **UK English Compliance**
- [ ] All "normalize" → "normalise"
- [ ] All "color" → "colour"
- [ ] All "while" → "whilst" (where appropriate)
- [ ] All "analyze" → "analyse"
- [ ] Date format: DD Month YYYY (e.g., 18 December 2025)

### **Technical Accuracy**
- [ ] All equations/formulae correct
- [ ] All code snippets formatted properly
- [ ] All tables formatted properly
- [ ] All citations present in references
- [ ] All cross-references working

### **Figures and Tables**
- [ ] Figure 5.1 generated and inserted
- [ ] Figure 5.2 generated and inserted
- [ ] Figure 5.3 generated and inserted
- [ ] Figure 5.4 generated and inserted
- [ ] Figure 5.5 generated and inserted
- [ ] All figure captions present
- [ ] All tables have captions
- [ ] Figures referenced in text (e.g., "as shown in Figure 5.1...")

---

## Distinction-Level Checklist (70-100%)

Based on evaluation criteria analysis:

### **Research Quality (30%)**
- [x] Clear research questions (RQ1-RQ4 with hypotheses)
- [x] Original contribution (SRS metric, auto-taxonomy, honest evaluation)
- [x] Rigorous methodology (fixed seeds, decision gates, robustness tests)
- [x] Critical analysis (ceiling effects, semantic loss, integration patterns)

### **Technical Implementation (25%)**
- [x] Production-ready system (sklearn baseline, hybrid architecture)
- [x] Reproducible code (pinned dependencies, fixed seeds)
- [x] Scalable design (hybrid graph-vector, sub-ms latency)
- [x] Documented architecture (Chapter 4 complete)

### **Evaluation and Results (20%)**
- [x] Honest evaluation (accuracy + SRS + latency + robustness)
- [x] Multiple metrics (micro-F1, macro-F1, HP, AtP, AP, RTF)
- [x] Robustness testing (taxonomy removal, unit noise)
- [x] Error analysis (per-class breakdowns, failure modes)

### **Writing and Presentation (15%)**
- [x] Clear structure (7 chapters, logical flow)
- [x] Academic tone (UK English, formal style)
- [x] Critical discussion (limitations, threats to validity)
- [x] Proper citations (26+ references)

### **Originality and Impact (10%)**
- [x] Novel metric (SRS: HP+AtP+AP+RTF)
- [x] Practical contribution (auto-taxonomy, pattern-based rules)
- [x] Transferable insights (multi-domain applicability)
- [x] Production readiness (operational considerations, SLOs)

---

## Timeline for Final Assembly

**Estimated Time**: 8-12 hours

1. **Hour 1-2**: Generate figures from Python code
2. **Hour 3-5**: Assemble Word document (copy all chapters)
3. **Hour 6-7**: Format document (headings, fonts, line spacing)
4. **Hour 8-9**: Insert figures and create captions
5. **Hour 10-11**: Create references section from Literature Review PDF
6. **Hour 11-12**: Create appendices (code listings, tables)
7. **Final checks**: Update table of contents, spell check, generate PDF

---

## File Locations Quick Reference

| Component | File Path |
|-----------|-----------|
| Abstract | `docs/thesis/Abstract.md` |
| Chapter 1 | `docs/thesis/Chapter_1_Introduction.md` |
| Chapter 2 | `docs/thesis/Chapter_2_Literature_Review.md` |
| Chapter 3 | `docs/thesis/Chapter_3_Methodology.md` |
| Chapter 4 | `docs/thesis/Chapter_4_Implementation.md` |
| Chapter 5 | `docs/thesis/Chapter_5_Results.md` |
| Chapter 6 | `docs/thesis/Chapter_6_Discussion.md` |
| Chapter 7 | `docs/thesis/Chapter_7_Conclusion.md` |
| Figure Specs | `docs/thesis/Chapter_5_Figure_Specifications.md` |
| Lit Review PDF | `Project Docs/Integrating Knowledge Graphs with Multi-Modal Machine Learning- Literature Review.pdf` |
| Project Spec PDF | `Project Docs/Project specification.pdf` |
| Methodology Source | `docs/01_METHODOLOGY.md` |
| Evaluation Sheet | `docs/EvaluationSheet_v1.md` |
| M10 Report | `docs/M10_SINGLE_SEED_VALIDATION_REPORT.md` |

---

## Next Steps

1. **Generate Figures**: Run Python code from `Chapter_5_Figure_Specifications.md`
2. **Extract References**: Copy from Literature Review PDF pages 12-14
3. **Create Appendices**: Extract code and tables from source files
4. **Assemble Word Document**: Follow assembly instructions above
5. **Quality Check**: Complete all checklist items
6. **Submit**: Generate PDF and submit according to university guidelines

---

**Status**: All major components complete. Thesis ready for final assembly into Word/PDF format for submission.

**Estimated submission readiness**: 8-12 hours of formatting and assembly work remaining.
