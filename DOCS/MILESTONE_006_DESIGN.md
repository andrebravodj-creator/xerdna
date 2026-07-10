# MILESTONE 006 DESIGN — The Biological Reasoning Core

**Constitutional basis:** this is a Level-5 Architecture-stage artifact (MASTER_CONTEXT.md Article I, Article XII stage 2), implementing BIOLOGICAL_REASONING_CONSTITUTION.md in full, under GRAPH/SCHEMA.md's Evidence, Confidence, Hypothesis, and Prediction Models, and governed by DOCS/IMPLEMENTATION_POLICY.md. Per Article XVIII, item 3 of the constitution: this document states explicitly, for every capability it defines, which Article of the constitution that capability implements. Silence on an applicable Article is treated as non-compliance, not omission.

**What this is not, stated first because it is the single most important scope boundary this milestone has:** the Biological Reasoning Core is not an AI model. It generates no hypotheses, performs no inference over unstructured text, calls no language model, and makes no judgment call a domain expert would recognize as "reasoning" in the colloquial sense. It is a deterministic computation and enforcement layer — every function in it, given the same input, produces the same output, every time, with no randomness and no learned parameters. Its job is to compute the properties a future AI component's output *must* have to be constitutionally admissible, and to refuse admission when those properties don't hold. The AI reasons. This layer checks the AI's arithmetic.

## 1. Why This Layer Exists, and Where It Sits

Milestone 002 built the Insertion Gate — the only legal way to write a record, enforcing GRAPH/SCHEMA.md's structural rules (tier validity, provenance completeness, tier-restricted promotion paths). The Gate is deliberately ignorant of biology. It does not know that a `research_hypothesis` combining three inputs of different tiers must inherit the weakest one; it only knows that a `research_hypothesis` row needs a `claim` and a `reasoning` field populated. That gap is not a defect in the Gate — Milestone 002 was never designed to close it, and closing it there would have coupled structural validation to scientific judgment in a way MASTER_CONTEXT.md Article IV's extension discipline warns against.

The Biological Reasoning Core is the layer that closes that gap, and it sits in a specific place in the pipeline a future AI component will use:

```
   Future AI Component            Biological Reasoning Core            Insertion Gate
  (not built; out of scope    →  (Milestone 006; deterministic,   →  (Milestone 002;
   for this milestone)            constitutional enforcement)         structural enforcement)
        proposes                       computes + validates                writes
```

**Rule, stated as the architectural spine of this whole design:** an AI component never calls `gate.py` directly with a derived or combined claim. It calls the Reasoning Core first. The Reasoning Core computes the claim's correct tier, confidence type, and eligibility, and only then — if the claim passes — does a write reach the Gate, through the Gate's existing, unmodified functions. The Reasoning Core adds a mandatory checkpoint; it does not add a second way to write to the graph, and it performs no writes of its own. (BIOLOGICAL_REASONING_CONSTITUTION.md Article XVIII, item 1: no component's design may create pressure toward the constitution's violations — a reasoning layer with its own write path would be exactly that pressure, since it would let an AI component route around the Core's own checks by writing directly.)

## 2. The Reasoning Pipeline

Conceptually, every future AI-proposed claim moves through five deterministic stages before it may ever reach the Gate. This milestone designs all five; it implements only the first, per the instruction to build 006A alone.

| Stage | Question it answers | Constitution Article(s) | Sub-milestone |
|---|---|---|---|
| 1. Tier & Confidence Propagation | Given the tiers/confidence-types of a claim's inputs, what tier and confidence-type may the derived claim carry? | II, III(5), XIII | **006A — implemented this milestone** |
| 2. Contradiction Detection | Does this claim structurally conflict with existing `established_evidence`? | VIII | 006B |
| 3. Hypothesis Eligibility | Does a candidate hypothesis meet the constitution's admissibility bar (falsifiable, dual-evidenced, non-self-resolving)? | VI, XV | 006C |
| 4. Causal/Correlational Boundary Check | Does a candidate causal claim meet the disclosure and evidentiary bar Article XII sets, beyond GRAPH/SCHEMA.md's existing E2 predicate check? | XII | 006D |
| 5. Explainability Trace Construction | Can the claim's full derivation be walked and audited by a human expert? | X, XI | 006E |

No stage generates content. Every stage either returns a computed property (stage 1), a boolean-or-reasoned-rejection (stages 2–4), or a structural trace of already-existing data (stage 5).

## 3. Evidence Propagation (006A)

**Constitutional basis:** GRAPH/SCHEMA.md's Scientific Integrity Constraint 3 ("propagate the weakest tier among its inputs... never round up to a stronger tier than its evidence supports") already states the rule informally. BIOLOGICAL_REASONING_CONSTITUTION.md does not weaken or restate it; it makes it a permanent, load-bearing constraint on every future AI component (Article XVIII).

**The rule, made precise:** the three tiers have a strict strength ordering — `established_evidence` > `computational_prediction` > `research_hypothesis`. When an AI component derives a new claim from N existing records, the derived claim's tier is the *weakest* (least certain) tier among the N inputs, never higher. This is a total order and a pure function: `weakest_tier(tiers: list[Tier]) -> Tier`.

**Why this is deterministic and belongs in this layer, not in an AI component:** there is no scientific judgment involved in this computation — it is arithmetic over an ordering the constitution and the schema have already fixed. An AI component that computed its own tier-propagation, even correctly, would be re-implementing a constitutional rule inside a non-deterministic system, which is exactly the kind of drift Article XX exists to prevent ("no future implementation... is grounds to quietly narrow an Article"). Centralizing it here means every future AI component gets it identically right, by construction, forever.

## 4. Confidence Propagation (006A)

**Constitutional basis:** BIOLOGICAL_REASONING_CONSTITUTION.md Article XIII ("no AI component may present a confidence value as calibrated unless..."); GRAPH/SCHEMA.md's Anti-Hallucination Rule 6 ("confidence is never invented to fill a required field").

**The rule, made precise:** `confidence_type` has two values, `numeric` and `qualitative`, plus the possibility of no confidence at all (an `established_evidence` input carries none). When combining confidence-bearing inputs:
- If any input's confidence is `qualitative`, the derived claim's confidence must be `qualitative` — numeric precision is never manufactured from a qualitative input, regardless of how many numeric inputs surround it.
- If all confidence-bearing inputs are `numeric`, the derived claim's confidence may be `numeric` — but this layer does not compute *what* numeric value results (that is a statistical/domain question belonging to whatever AI component or method is doing the combining, and must itself be named and versioned per Article V); it only enforces the type-safety boundary.
- If no input carries confidence at all (a claim derived purely from `established_evidence` records, none of which carry a confidence field), the derived claim carries none either, unless the derivation itself introduces a new source of uncertainty — that case belongs to 006C (hypothesis eligibility), not to this primitive.

## 5. Uncertainty Propagation (Designed Here, Implemented in a Later Sub-Milestone)

**Constitutional basis:** Article VII (aleatory vs. epistemic uncertainty).

GRAPH/SCHEMA.md's Confidence Model has no field distinguishing *why* a confidence value is what it is — whether the uncertainty is epistemic (reducible, more data would shrink it) or aleatory (irreducible, inherent to the biological system's own stochasticity). This is a real, load-bearing gap between what the newly-ratified constitution requires and what the current schema can express — flagged here explicitly, per this project's standing discipline, rather than assumed solved.

**Designed shape, for 006B or a dedicated sub-milestone:** a `confidence_basis_kind` classification (`epistemic` | `aleatory` | `mixed`) attached wherever `confidence_type: qualitative` already requires a `basis` string (Anti-Hallucination Rule 6) — the classification and the free-text basis are complementary, not redundant: the classification lets a downstream consumer mechanically distinguish the two kinds without parsing prose. This is not implemented in 006A. No code in this milestone references it.

## 6. Contradiction Propagation (Designed Here, Implemented in 006B)

**Constitutional basis:** Article VIII; GRAPH/SCHEMA.md's E4 rule (conflicting `established_evidence` is valid, preserved, never resolved at ingestion).

**Designed shape:** a deterministic structural-contradiction detector — given a candidate claim (subject, predicate, object) and the set of existing `established_evidence` associations sharing the same subject/object, determine whether any existing association asserts a predicate structurally incompatible with the candidate (e.g., a directionally opposite `regulates` qualifier, or an explicit negation). This is *structural* detection only — recognizing that two records formally conflict — never *semantic* adjudication of which one is right. Per Article VIII, item 2, explaining *why* two established findings disagree is itself a `research_hypothesis`-tier act belonging to a future AI component, never to this deterministic layer.

## 7. Hypothesis Eligibility (Designed Here, Implemented in 006C)

**Constitutional basis:** Article VI (motivated by evidence, dual-evidenced, non-self-resolving); Article XV (falsifiability).

**Designed shape:** `check_hypothesis_eligibility(candidate) -> EligibilityResult` — a deterministic pre-check run *before* `gate.insert_hypothesis()` is ever called, verifying:
1. `supporting_evidence` references at least one real, existing graph record (Article VI, item 1) — not merely a non-empty string, but a resolvable reference.
2. `contradicting_evidence` is populated, or `none_found_as_of` is explicit — already enforced by `gate.insert_hypothesis()` itself; this stage re-verifies it as a named, citable constitutional check rather than an incidental side effect of a schema constraint.
3. A falsification condition is present and is not vacuous (Article XV) — **this requires a schema field that does not yet exist.** GRAPH/SCHEMA.md's Hypothesis Model has no `falsification_condition` column. This is the second explicit schema gap this design surfaces (after uncertainty-kind, Section 5) and is likewise not closed by this milestone — 006C's own design, when it is taken up, must either extend the schema (through the full governance discipline, not silently) or the constitution's Article XV requirement remains unenforceable in practice, a state this design does not consider acceptable to leave indefinitely, only acceptable to leave *named* until 006C.
4. The candidate is not, itself, generated by the same process that would resolve it (Article VI, item 5) — checkable only by convention (`generated_by` differs from whatever identifier a resolution process would use) until a stronger mechanism is designed; flagged as a weaker check than the others, honestly, rather than overstated.

## 8. Causal Reasoning and Correlation Boundaries (Designed Here, Implemented in 006D)

**Constitutional basis:** Article XII in full.

`gate.py` already enforces E2's minimum floor: a `biolink:causes` predicate requires `source_span` populated (Milestone 002). Article XII requires more than a populated field — it requires that the *reasoning* behind a causal claim actually reflects considerations like temporality, dose-response, mechanistic plausibility, and the availability (or absence) of an actual intervention. **Designed shape:** a `CausalClaimDisclosure` structure a future AI component must populate and attach to any candidate `causes` predicate, naming which of Article XII's criteria it evaluated and what it found — the Reasoning Core's job is to verify the structure is *complete* (every criterion addressed, none silently skipped) and that no criterion's answer is self-contradictory (e.g., claiming "temporality: cause precedes effect" while the cited evidence's timestamps show the reverse) — not to judge whether the causal hypothesis is *correct*. Correctness is a scientific judgment; completeness and internal consistency of the disclosure are deterministic properties this layer can and must check.

## 9. Explainability and Traceability (Designed Here, Implemented in 006E)

**Constitutional basis:** Article X (explainability), Article XI (provenance as epistemic warrant).

**Designed shape:** `build_derivation_trace(claim_id) -> DerivationTrace` — given any claim this Core helped admit, deterministically walk backward through every input that contributed to its tier, confidence, and eligibility determinations, returning a structure a human expert can inspect without needing to re-run any AI component. This is graph traversal, not reasoning — the same category of operation as `identity.find_matching_xerdna_ids()` (Milestone 005), applied to derivation history instead of xref identity. Every function in 006A already returns a `reasoning: str` field alongside its computed result (Section 10) — 006E's job is to compose those per-function explanations into one walkable chain for an arbitrarily deep derivation, not to invent a new explanation mechanism.

## 10. Explainability as a Design Convention, Not Just a Future Feature

Every function this milestone actually implements returns a small, immutable result object carrying both the computed value *and* a human-readable `reasoning` string stating why that value was computed — never a bare value. This is 006A's own concrete, minimal instance of Article X, and it is the convention every later sub-milestone (006B–006E) inherits: **no function in the Biological Reasoning Core ever returns an answer without also returning why.** A future AI component, or a future Core function, that only returns a value has not satisfied Article X regardless of how correct the value is.

## 11. Reproducibility

**Constitutional basis:** Article XIV.

Every function in 006A is a pure function: no randomness, no wall-clock reads, no I/O, no hidden state, no network access. Given identical inputs, it produces byte-identical output, always. This satisfies Article XIV trivially for this sub-milestone specifically — it is stated here explicitly because it will *not* remain trivial once a future sub-milestone or AI component introduces genuinely non-deterministic methods (Article V's tier 4, LLM-based inference); this design commits, now, that even then, the Reasoning Core's own *checking* functions must remain deterministic — a non-deterministic method may be checked, but the checker itself is never permitted to become non-deterministic, or Article XIV's guarantee collapses at the one place it matters most.

## 12. Constitutional Enforcement Map

| Reasoning Core capability | Constitution Article(s) | Sub-milestone | Status |
|---|---|---|---|
| Tier propagation (weakest-tier-wins) | II, III(5) | 006A | Implemented this milestone |
| Confidence-type propagation | XIII, Anti-Hallucination Rule 6 | 006A | Implemented this milestone |
| Every function returns value + reasoning | X | 006A | Implemented this milestone |
| Purity / no hidden state | XIV | 006A | Implemented this milestone (by construction) |
| Uncertainty-kind (aleatory/epistemic) tagging | VII | 006B+ | Designed (Section 5); schema gap flagged |
| Structural contradiction detection | VIII | 006B | Designed (Section 6) |
| Hypothesis eligibility (incl. falsifiability) | VI, XV | 006C | Designed (Section 7); schema gap flagged |
| Causal claim disclosure completeness check | XII | 006D | Designed (Section 8) |
| Derivation trace construction | X, XI | 006E | Designed (Section 9) |
| Human override / non-resistance | XVI | N/A — behavioral constraint on future AI components themselves, not a function this deterministic layer computes; the Core's contribution is only that no path exists for an AI component to bypass it, per Section 1's pipeline rule | — |
| Laboratory validation gating | XVII | N/A — already enforced structurally by `gate.py`'s `promote_prediction()`/`resolve_hypothesis()` tier-restriction checks (Milestone 002); this milestone adds no new mechanism here | — |

## 13. What Milestone 006A Implements

Per instruction, only Section 3 and Section 4 (tier propagation, confidence-type propagation) plus Section 10's explainability convention and Section 11's purity guarantee — the two deterministic primitives named as the reasoning pipeline's first stage, nothing else. Sections 5–9 are design only, explicitly not implemented, tracked as 006B–006E for future engineering milestones.

### 13.1 Module

`GRAPH/engine/reasoning/tier_propagation.py`, in a new `GRAPH/engine/reasoning/` subpackage — reserving the package for 006B–006E's future modules without pre-building them.

### 13.2 Functions

```
TIER_STRENGTH: dict[str, int]   # established_evidence=3, computational_prediction=2, research_hypothesis=1

TierPropagationResult(tier: str, reasoning: str)
weakest_tier(tiers: list[str]) -> TierPropagationResult

ConfidenceTypePropagationResult(confidence_type: str | None, reasoning: str)
propagate_confidence_type(confidence_types: list[str | None]) -> ConfidenceTypePropagationResult
```

Both are pure functions over plain Python values — no database connection, no graph access, no gate.py dependency. This is deliberate: tier and confidence-type propagation are properties of a *set of tier/confidence values*, not of the graph itself. A future caller (an AI component, or 006B–006E) is responsible for reading the actual input records' tiers/confidence-types from the graph and passing them in; this module does not reach into storage to fetch them itself, keeping it the smallest possible deterministic unit.

### 13.3 Task Breakdown

| # | Task | Files | Validation |
|---|---|---|---|
| 1 | `weakest_tier()` + `TierPropagationResult` | `GRAPH/engine/reasoning/__init__.py`, `tier_propagation.py` (new) | All orderings of 1–4 input tiers produce the correct weakest result; empty input and unknown tier both rejected with a clear error |
| 2 | `propagate_confidence_type()` + `ConfidenceTypePropagationResult` | `tier_propagation.py` (extended) | Qualitative-dominance, all-numeric, no-confidence, and mixed/invalid cases all produce the correct result or a clear rejection |
| 3 | Full validation: purity, explainability convention, constitutional traceability | `GRAPH/engine/tests/test_milestone_006.py` (new) | Every result carries a non-empty `reasoning`; repeated calls are byte-identical; full offline suite green |

## 14. What This Design Is Not

- **Not an AI component.** No model, no LLM call, no learned parameter, anywhere in this milestone.
- **Not a hypothesis generator.** Nothing in 006A proposes a claim; every function takes an already-proposed set of tiers/confidence-types as input.
- **Not a replacement for the Insertion Gate.** The Gate is unmodified by this milestone and remains the only legal write path.
- **Not complete.** Sections 5, 6, 7, 8, and 9 are designed, not built. Two schema gaps (uncertainty-kind, falsification-condition) are named and explicitly deferred, not silently assumed solved.

## Next Steps (Not Performed Here)

Implement Milestone 006A per Section 13, validate fully offline, stop automatically per instruction. Sub-milestones 006B–006E remain design-only until separately kicked off, each requiring its own implementation plan the way every prior milestone has.
