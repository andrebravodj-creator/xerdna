"""
The Biological Reasoning Core -- the deterministic reasoning layer every
future AI component inside XERDNA must obey.

Traces to: BIOLOGICAL_REASONING_CONSTITUTION.md (ratified, co-equal with
VISION.md at Level 1 of MASTER_CONTEXT.md Article I); DOCS/MILESTONE_006_DESIGN.md.

This package is NOT an AI model. It generates no hypotheses, performs no
inference, calls no language model. Every function in it is pure and
deterministic: same input, same output, always, forever. It computes the
properties a future AI-proposed claim must have to be constitutionally
admissible, and refuses admission when they don't hold. The AI reasons.
This package checks the AI's arithmetic.

Milestone 006A implements only tier and confidence-type propagation
(tier_propagation.py). Contradiction detection, hypothesis eligibility,
causal-claim disclosure checking, and derivation-trace construction are
designed in DOCS/MILESTONE_006_DESIGN.md but not yet implemented -- this
package is reserved for their future modules (006B-006E), not pre-built.
"""
