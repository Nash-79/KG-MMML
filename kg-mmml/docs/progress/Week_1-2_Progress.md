# Week 1-2 Progress Report

**Period:** Weeks 1-2  
**Focus:** Literature Review & Project Specification

---

## Summary

The first two weeks focused on responding to literature review feedback and finalizing the project specification. We narrowed the scope, strengthened the critical analysis, added measurable targets, and set up the foundational tooling and repository structure.

**No blockers.** Model training intentionally starts in Weeks 3-4 after metric instrumentation is in place.

---

## Literature Review Improvements

**Scope Refinement**  
Narrowed from broad KG survey to open-world retrieval and zero-shot classification with domain-agnostic approaches.

**Critical Analysis**  
Rewrote sections to be critical rather than descriptive. Added explicit trade-offs:
- KG-as-features vs joint learning approaches
- Monolithic vs hybrid architectures
- Generic vs domain-specific knowledge graphs

**Worked Examples**  
Added concrete examples to illustrate key concepts:
- Semantic retention measurement methodology
- Hybrid system break-point analysis
- Domain vs generic KG comparison

**Measurable Targets**  
Introduced quantitative targets to carry into implementation:
- SRS improvement: +≥25% or +0.10 absolute
- Latency reduction: p95 −≥30%
- Robustness: ≤10% degradation under perturbation
- Accuracy: within −2 points of pure neural baseline

**Documentation**  
Created glossary of abbreviations for clarity.

---

## Project Specification

**Problem Statement**  
KG-MMML integrations often flatten semantic relations, struggle with operational performance, and over-rely on accuracy metrics without considering semantic fidelity or explainability.

**Project Aim**  
Build a pragmatic, reproducible framework that preserves semantic relationships, meets performance service-level objectives, and provides faithful explanations.

**Objectives & Research Questions**  
Finalized five measurable objectives aligned with literature review findings. Each has clear decision gates and acceptance criteria.

**Significance**  
Clarified cross-domain benefits and provided decision rules for practitioners choosing between approaches.

---

## Planning & Repository Structure

**24-Week Project Plan**  
Created detailed plan mapped 1:1 to marking rubric components:
- Specification
- Literature Review
- Methodology
- Results
- Conclusion
- Structure & Presentation
- Quality of Management

**Repository Scaffold**  
Established clean directory structure:
- `src/` - Source code
- `data/` - Generated data (git-ignored)
- `configs/` - Experiment configurations
- `notebooks/` - Analysis notebooks
- `reports/` - Results and metrics
- `docs/` - Documentation

**Reproducibility Policy**  
- Fixed random seeds for all experiments
- Configuration files for all hyperparameters
- Pinned dependencies and versions

**Change Log**  
Documented all deviations from original plan with explanations (primarily due to feedback adoption).

---

## Source Control & Governance

**GitHub Repository**  
Private repository initialized with the published scaffold structure.

**Branching Model**  
- Feature branches for development
- KG-MMML integration branch for testing
- Protected main branch for releases

**Repository Hygiene**  
- `.gitignore` excludes data snapshots and caches
- `.gitattributes` normalizes line endings
- Basic lint/test workflow added
- Releases will include reproducible artifacts (config + commands + snapshot tags)

**Privacy**  
Repository is private. URL recorded in project plan for audit trail.

---

## Deliverables

**Documentation**
- Updated Literature Review with feedback incorporated
- Finalized Project Specification
- 24-week project plan with rubric mapping
- Glossary of abbreviations
- Change Log

**Infrastructure**
- GitHub repository with clean structure
- Reproducibility policy established
- Branch protection and workflow automation
- Config templates and seed policy

---

## Next Steps (Week 3-4)

**Data Pipeline**  
Build automated SEC EDGAR data acquisition pipeline.

**KG Schema Design**  
Design and implement knowledge graph schema with node and edge types.

**SRS Framework**  
Implement Semantic Relationship Score computation framework.

**Repository Polish**  
Finalize directory structure and documentation templates.
