# Progress Report PR1 — Weeks 1–2

## 1) Summary

The first fortnight focused on two assessed foundations: (i) acting on literature-review feedback (narrowed scope; stronger critique; worked examples; measurable targets), and (ii) finalising the Project Specification (problem, aim, objectives, RQs, significance). I created a rubric-mapped plan, a glossary of abbreviations, and a change log explaining why the plan now differs from the original. Baseline tooling (repo, config, seeds policy) were also set up. Model training intentionally starts in Weeks 3–4 after metric instrumentation is locked. No blockers.

## 2) Activities completed (Weeks 1–2)

### 2.1 Literature review (feedback acted on)

Re-scoped from broad survey to open-world retrieval & zero-shot classification (domain-agnostic).

Rewrote sections to be critical rather than descriptive, with explicit trade-offs (KG-as-features vs joint; monolithic vs hybrid; generic vs domain KGs).

Added worked examples (semantic-retention measurement; hybrid break-point; domain vs generic KG).

Introduced measurable targets to carry forward into the project (SRS +≥25% / +0.10; p95 −≥30%; robustness ≤10% degradation; accuracy within −2 points).

Created a glossary of abbreviations for assessor clarity.

### 2.2 Project Specification

Problem: KG–MMML integrations often flatten relations, struggle operationally, and over-rely on accuracy metrics.

Aim: A pragmatic, reproducible framework that preserves semantics, meets performance SLOs, and provides faithful explanations.

Objectives & RQs: Finalised, measurable, and aligned to the Literature Review.

Significance: Clarified cross-domain benefits and practitioner decision rules.

### 2.3 Planning, governance and structure

Built a 24-week project plan mapped 1:1 to the marking rubric (spec, Literature Review, methodology, results, conclusion, structure/presentation, quality of management).

Created repository scaffold (src/, data/, configs/, notebooks/, reports/, docs/), seeded reproducibility policy (fixed seeds, config files).

Logged all deviations from the original in a Change Log (why plan changed: feedback adoption).

### 2.4 Source control & reproducibility (GitHub, private)

A private GitHub repository has been initialised and structured to the published scaffold: src/, datasets/, data/ (git-ignored), configs/, notebooks/, reports/, docs/.

Branching model: feature branches → KG-MMML integration branch → protected main.

Governance: .gitignore excludes data/snapshots; .gitattributes normalises line endings; Change Log maintained; seeds/configs pinned.

CI hygiene: basic lint/test workflow added; releases will attach a reproducible artefact (config + commands + snapshot tag).

Repository privacy: private for now; URL recorded in the plan for audit.
