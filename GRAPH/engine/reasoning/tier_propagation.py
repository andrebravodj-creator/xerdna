"""
Tier and confidence-type propagation -- the deterministic core of
Engineering Milestone 006A.

Traces to:
  BIOLOGICAL_REASONING_CONSTITUTION.md Article II item 4, Article III
    item 5, Article X (explainability), Article XIII (confidence and
    calibration), Article XIV (reproducibility).
  GRAPH/SCHEMA.md Scientific Integrity Constraint 3 ("propagate the
    weakest tier among its inputs... never round up to a stronger tier
    than its evidence supports") and Anti-Hallucination Rule 6
    ("confidence is never invented to fill a required field").
  DOCS/MILESTONE_006_DESIGN.md Sections 3, 4, 10, 11.

Every function here is pure: no randomness, no I/O, no database
connection, no hidden state. Given the same input, the same output is
returned every time (Article XIV). Every result carries both the computed
value and a human-readable explanation of why (Article X) -- no function
in this module ever returns a bare value.
"""

from dataclasses import dataclass

# Strength ordering, strongest to weakest. The derived tier of a claim
# built from multiple inputs is always the WEAKEST tier among them --
# never rounded up (GRAPH/SCHEMA.md Scientific Integrity Constraint 3).
TIER_STRENGTH: dict[str, int] = {
    "established_evidence": 3,
    "computational_prediction": 2,
    "research_hypothesis": 1,
}

VALID_CONFIDENCE_TYPES = frozenset({"numeric", "qualitative"})


class ReasoningCoreError(ValueError):
    """Raised when an input to a Biological Reasoning Core function is malformed or empty."""


@dataclass(frozen=True)
class TierPropagationResult:
    tier: str
    reasoning: str


@dataclass(frozen=True)
class ConfidenceTypePropagationResult:
    confidence_type: str | None
    reasoning: str


def weakest_tier(tiers: list[str]) -> TierPropagationResult:
    """
    Given the evidence_tier of every input that contributed to a derived
    claim, return the tier the derived claim may carry: the weakest
    (least certain) among them, never stronger.

    BIOLOGICAL_REASONING_CONSTITUTION.md Article II item 4; GRAPH/SCHEMA.md
    Scientific Integrity Constraint 3.
    """
    if not tiers:
        raise ReasoningCoreError("weakest_tier requires at least one input tier")

    unknown = [t for t in tiers if t not in TIER_STRENGTH]
    if unknown:
        raise ReasoningCoreError(
            f"unknown evidence tier(s) {unknown!r}; must be one of {sorted(TIER_STRENGTH)}"
        )

    result = min(tiers, key=lambda t: TIER_STRENGTH[t])
    if len(set(tiers)) == 1:
        reasoning = f"all {len(tiers)} input(s) are {result!r}; the derived claim inherits that single tier."
    else:
        reasoning = (
            f"inputs span {sorted(set(tiers), key=lambda t: TIER_STRENGTH[t])} (weakest to strongest); "
            f"the derived claim inherits the weakest, {result!r}, per Scientific Integrity Constraint 3 -- "
            f"a claim built partly from a {result!r} input is itself no stronger than {result!r}."
        )
    return TierPropagationResult(tier=result, reasoning=reasoning)


def propagate_confidence_type(confidence_types: list[str | None]) -> ConfidenceTypePropagationResult:
    """
    Given the confidence_type of every input to a derived claim (None for
    an input that carries no confidence at all, e.g. an established_evidence
    record), return the confidence_type the derived claim may carry.

    Rule: if any input's confidence is qualitative, the derived claim's
    confidence must be qualitative too -- numeric precision is never
    manufactured from a qualitative input, regardless of how many numeric
    inputs surround it (BIOLOGICAL_REASONING_CONSTITUTION.md Article XIII;
    Anti-Hallucination Rule 6).
    """
    present = [c for c in confidence_types if c is not None]

    invalid = [c for c in present if c not in VALID_CONFIDENCE_TYPES]
    if invalid:
        raise ReasoningCoreError(
            f"unknown confidence_type(s) {invalid!r}; must be one of {sorted(VALID_CONFIDENCE_TYPES)} or None"
        )

    if not present:
        return ConfidenceTypePropagationResult(
            confidence_type=None,
            reasoning="no input carries a confidence value (all inputs are established_evidence or otherwise "
                      "confidence-free); the derived claim carries none either.",
        )

    if "qualitative" in present:
        return ConfidenceTypePropagationResult(
            confidence_type="qualitative",
            reasoning=(
                f"{present.count('qualitative')} of {len(present)} confidence-bearing input(s) are qualitative; "
                f"the derived claim's confidence must be qualitative -- numeric precision is never manufactured "
                f"from a qualitative input (Article XIII; Anti-Hallucination Rule 6)."
            ),
        )

    return ConfidenceTypePropagationResult(
        confidence_type="numeric",
        reasoning=f"all {len(present)} confidence-bearing input(s) are numeric; the derived claim may carry a "
                  f"numeric confidence -- this function does not compute its value, only its type-safety.",
    )
