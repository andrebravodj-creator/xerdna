# VISION

> Discover the Unknown Within Life.

**This is a constitutional document.** It defines XERDNA's mission, philosophy, and principles at the highest level of authority. See [MASTER_CONTEXT.md](MASTER_CONTEXT.md) Article III for how these documents may be amended, and Article I for the authority hierarchy that binds every future technical decision to what is written here.

---

## Article I — Mission

To organize humanity's biological knowledge and accelerate scientific discovery through artificial intelligence.

## Article II — Origin & Vision

XERDNA started as an AI primer design idea — a tool to help researchers design DNA primers faster.

The vision evolved into something much larger.

**XERDNA is not a primer application. XERDNA is a Biological Intelligence Platform.**

Its long-term mission is to organize biological knowledge, connect scientific evidence, assist researchers, and accelerate discovery — while respecting the scientific method. Over its lifetime, XERDNA becomes:

- A single, living map of biological knowledge — genomes, genes, proteins, pathways, evidence, and the literature that supports it.
- A reasoning system that finds relationships, contradictions, and gaps humans haven't connected yet.
- A generator of evidence-ranked hypotheses that researchers can pursue, not conclusions they should trust blindly.
- A shared intelligence layer that universities, hospitals, biotech, and pharma can build on instead of re-deriving.

See [ROADMAP.md](ROADMAP.md) for how these capabilities are sequenced across phases.

## Article III — What XERDNA Is Not

- XERDNA is not a lab. It never replaces laboratory validation.
- XERDNA is not an oracle. It never claims discoveries — only humans and experiments confirm those.
- XERDNA is not a single product. It is infrastructure meant to outlive any one product built on top of it.
- XERDNA is not done at any named phase. There is no "done" — see Article IX.

## Article IV — The Evidence Principles

Biology is not a domain where confident-sounding output is good enough. A platform that blurs the line between "we measured this" and "a model predicted this" produces false confidence at civilizational scale. XERDNA's credibility depends on never letting that line blur — in the graph, the reasoning engine, the UI, or any API response.

Every piece of biological information XERDNA touches must be traceable to exactly one of three tiers:

| Tier | Meaning | Example |
|---|---|---|
| **Established Evidence** | Peer-reviewed, reproduced, or otherwise scientifically validated fact | "Gene X is associated with pathway Y (source: study, DOI)" |
| **Computational Prediction** | Output of a model, simulation, or algorithm — not yet validated | "Model predicts protein Z binds site W (confidence: 0.72)" |
| **Research Hypothesis** | A generated, evidence-ranked question worth investigating | "Hypothesis: pathway A may modulate disease B (supporting/contradicting evidence attached)" |

These tiers are not a UI nicety layered on later — they are load-bearing, from the first phase onward. Anything that cannot cite its tier does not belong in the system.

## Article V — Scientific Principles

1. **The scientific method is not negotiable.** XERDNA accelerates the steps a scientist would take — it does not skip them.
2. **Hypotheses, never discoveries.** XERDNA generates evidence-ranked hypotheses for researchers to pursue or refute. It does not assert that something has been discovered, proven, or confirmed.
3. **Refutation is signal, not noise.** A contradicted hypothesis or a disproven prediction is exactly as valuable to record as a confirmed one — both narrow the space of what's true.
4. **Reproducibility over cleverness.** A finding that cannot be traced back to its source data and method is not a finding XERDNA surfaces.
5. **Absence of evidence is data.** Research gaps — areas where evidence is surprisingly thin — are first-class outputs, not omissions.

## Article VI — AI Principles

XERDNA uses artificial intelligence throughout its reasoning, hypothesis, and simulation layers. That use is bound by the following, permanently:

1. **Assist, never replace.** AI accelerates researchers. It does not substitute for laboratory validation, peer review, or scientific judgment at any phase.
2. **No autonomous claims.** No AI component in XERDNA may assert a discovery, a validated fact, or a conclusion on its own authority. It may only produce output tagged with one of the three Evidence Tiers (Article IV).
3. **Method transparency.** Every computational prediction must name the model and version that produced it. An untraceable model output does not belong in the system.
4. **Explainability for hypotheses.** Every generated hypothesis must include the reasoning that produced it, not just the conclusion — a hypothesis without visible reasoning cannot be evaluated by a scientist and is therefore not useful.
5. **Human-in-the-loop by design.** Every phase of the roadmap, including the Autonomous Scientist (Phase 5) and Collective Intelligence (Phase 6), keeps a human or an experiment as the final arbiter of truth. Autonomy applies to research *effort* (reading, connecting, proposing), never to *validation*.

## Article VII — Ethical Principles

1. **Biosecurity first.** XERDNA will not be used to design, optimize, or assist the creation of pathogens, toxins, or biological agents intended to cause harm, and will not assist in circumventing dual-use research of concern (DURC) safeguards. This constraint is absolute and outranks any feature request or commercial interest, at every future phase.
2. **Privacy of clinical and genomic data.** Individual-level clinical, genomic, or patient data is handled under the strictest applicable privacy standard available at the time, not the most convenient one. Aggregated and de-identified data is preferred wherever it serves the same scientific purpose.
3. **Attribution as a first-class value.** Every piece of evidence traces back to the researchers, institutions, and publications that produced it. XERDNA is built on the work of the scientific community and must never obscure that lineage.
4. **Broad access over gatekeeping.** As XERDNA becomes an intelligence layer for universities, hospitals, biotech, pharma, diagnostics, and academia (Phase 7), it favors architectures that widen access to biological knowledge over ones that concentrate it artificially.
5. **Honesty about what the system is.** Users of XERDNA are always told, plainly, when they are looking at established evidence, a prediction, or a hypothesis. This is Article IV enforced as an ethical obligation, not just a data rule.

## Article VIII — Scientific Integrity as Supreme Constraint

When any future technical decision — data model, algorithm, interface, or business consideration — would blur the distinction in Article IV, that decision is rejected, regardless of what phase XERDNA is in or what would be more convenient to ship. Scientific integrity is not one design goal among several; it is the constraint every other goal is optimized within.

## Article IX — Permanent Architectural Rules

**"Build for 2,000 phases, not the next 20."**

The roadmap names phases today, but that count is a description of the current horizon, not a ceiling. Treat every architectural decision on load-bearing components — the knowledge graph, the evidence model, the provenance layer, entity identity — as if hundreds of future phases will be built on top of it by people not currently in the room:

- Prefer designs that can absorb new data types, new organisms, new modalities of evidence without a rewrite.
- Prefer provenance and traceability over convenience — a fact with no lineage is a liability decades from now, even if it saves time today.
- Prefer boring, well-understood foundations for anything load-bearing over anything clever that is hard to migrate away from.
- Do not optimize for the current phase's use case at the expense of the platform's ability to become the next phase's use case.

This is not a license to over-build every feature speculatively — a bug fix is still just a bug fix. It is a standard for the parts of the system everything else will stand on.

**"Scientific Constitution Before Code."**

No implementation — schema, database, ingestion pipeline, API, backend service, or interface — is authoritative until it is traceable to a ratified article in these constitutional documents. If technical work exposes a gap or conflict the constitution doesn't address, the constitution is amended first (see [MASTER_CONTEXT.md](MASTER_CONTEXT.md) Article III), and only then does the technical work resume. Architecture follows principle; principle is never retrofitted to justify architecture already built.

## Article X — Tagline

**XERDNA — Discover the Unknown Within Life.**
