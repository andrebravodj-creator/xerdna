"""
Validation framework for Engineering Milestone 006A -- Tier and
Confidence-Type Propagation (the Biological Reasoning Core's first
implemented primitives).

Traces to: DOCS/MILESTONE_006_DESIGN.md Section 13; BIOLOGICAL_REASONING_
CONSTITUTION.md Articles II, III, X, XIII, XIV.

Fully offline -- no network access, no database connection anywhere in
this file or the module it exercises (tier_propagation.py operates on
plain Python values only).

Standard library only (unittest).
"""

import inspect
import itertools
import unittest

from GRAPH.engine.reasoning import tier_propagation as tp


class TestWeakestTier(unittest.TestCase):
    def test_single_established_evidence(self):
        result = tp.weakest_tier(["established_evidence"])
        self.assertEqual(result.tier, "established_evidence")
        self.assertTrue(result.reasoning)

    def test_single_research_hypothesis(self):
        result = tp.weakest_tier(["research_hypothesis"])
        self.assertEqual(result.tier, "research_hypothesis")

    def test_established_plus_prediction_yields_prediction(self):
        result = tp.weakest_tier(["established_evidence", "computational_prediction"])
        self.assertEqual(result.tier, "computational_prediction")

    def test_established_plus_hypothesis_yields_hypothesis(self):
        result = tp.weakest_tier(["established_evidence", "research_hypothesis"])
        self.assertEqual(result.tier, "research_hypothesis")

    def test_prediction_plus_hypothesis_yields_hypothesis(self):
        result = tp.weakest_tier(["computational_prediction", "research_hypothesis"])
        self.assertEqual(result.tier, "research_hypothesis")

    def test_all_three_tiers_yields_hypothesis(self):
        result = tp.weakest_tier(["established_evidence", "computational_prediction", "research_hypothesis"])
        self.assertEqual(result.tier, "research_hypothesis")

    def test_order_of_inputs_does_not_matter(self):
        """Purity/determinism: every permutation of the same multiset produces the same result."""
        tiers = ["established_evidence", "computational_prediction", "research_hypothesis"]
        results = {tp.weakest_tier(list(perm)).tier for perm in itertools.permutations(tiers)}
        self.assertEqual(results, {"research_hypothesis"})

    def test_never_rounds_up(self):
        """Exhaustive check: no combination of 1-3 inputs ever produces a tier stronger than its weakest input."""
        all_tiers = list(tp.TIER_STRENGTH)
        for r in (1, 2, 3):
            for combo in itertools.combinations_with_replacement(all_tiers, r):
                with self.subTest(combo=combo):
                    result = tp.weakest_tier(list(combo))
                    expected_strength = min(tp.TIER_STRENGTH[t] for t in combo)
                    self.assertEqual(tp.TIER_STRENGTH[result.tier], expected_strength)

    def test_empty_input_rejected(self):
        with self.assertRaises(tp.ReasoningCoreError):
            tp.weakest_tier([])

    def test_unknown_tier_rejected(self):
        with self.assertRaises(tp.ReasoningCoreError):
            tp.weakest_tier(["established_evidence", "not_a_real_tier"])

    def test_result_is_immutable(self):
        result = tp.weakest_tier(["established_evidence"])
        with self.assertRaises(AttributeError):
            result.tier = "computational_prediction"  # frozen dataclass


class TestPropagateConfidenceType(unittest.TestCase):
    def test_all_none_yields_none(self):
        result = tp.propagate_confidence_type([None, None])
        self.assertIsNone(result.confidence_type)
        self.assertTrue(result.reasoning)

    def test_all_numeric_yields_numeric(self):
        result = tp.propagate_confidence_type(["numeric", "numeric"])
        self.assertEqual(result.confidence_type, "numeric")

    def test_any_qualitative_yields_qualitative(self):
        result = tp.propagate_confidence_type(["numeric", "qualitative"])
        self.assertEqual(result.confidence_type, "qualitative")

    def test_all_qualitative_yields_qualitative(self):
        result = tp.propagate_confidence_type(["qualitative", "qualitative"])
        self.assertEqual(result.confidence_type, "qualitative")

    def test_none_mixed_with_numeric_ignores_none(self):
        result = tp.propagate_confidence_type([None, "numeric", "numeric"])
        self.assertEqual(result.confidence_type, "numeric")

    def test_none_mixed_with_qualitative_still_qualitative(self):
        result = tp.propagate_confidence_type([None, "numeric", "qualitative"])
        self.assertEqual(result.confidence_type, "qualitative")

    def test_qualitative_never_upgraded_regardless_of_numeric_majority(self):
        """Exhaustive: any presence of qualitative among up to 5 inputs always wins."""
        for n_numeric in range(5):
            inputs = ["numeric"] * n_numeric + ["qualitative"]
            with self.subTest(n_numeric=n_numeric):
                result = tp.propagate_confidence_type(inputs)
                self.assertEqual(result.confidence_type, "qualitative")

    def test_order_does_not_matter(self):
        results = {
            tp.propagate_confidence_type(list(perm)).confidence_type
            for perm in itertools.permutations(["numeric", "qualitative", None])
        }
        self.assertEqual(results, {"qualitative"})

    def test_empty_input_yields_none_not_error(self):
        # an empty list is a degenerate case of "no confidence-bearing inputs" -- not malformed
        result = tp.propagate_confidence_type([])
        self.assertIsNone(result.confidence_type)

    def test_invalid_confidence_type_rejected(self):
        with self.assertRaises(tp.ReasoningCoreError):
            tp.propagate_confidence_type(["numeric", "not_a_real_confidence_type"])

    def test_result_is_immutable(self):
        result = tp.propagate_confidence_type(["numeric"])
        with self.assertRaises(AttributeError):
            result.confidence_type = "qualitative"


class TestExplainabilityConvention(unittest.TestCase):
    """DOCS/MILESTONE_006_DESIGN.md Section 10: no function ever returns a bare value."""

    def test_weakest_tier_always_has_nonempty_reasoning(self):
        for combo_len in (1, 2, 3):
            for combo in itertools.combinations_with_replacement(tp.TIER_STRENGTH, combo_len):
                result = tp.weakest_tier(list(combo))
                self.assertIsInstance(result.reasoning, str)
                self.assertGreater(len(result.reasoning), 10)

    def test_confidence_propagation_always_has_nonempty_reasoning(self):
        cases = [[], [None], ["numeric"], ["qualitative"], ["numeric", "qualitative"], [None, "numeric"]]
        for case in cases:
            with self.subTest(case=case):
                result = tp.propagate_confidence_type(case)
                self.assertIsInstance(result.reasoning, str)
                self.assertGreater(len(result.reasoning), 10)


class TestPurityAndReproducibility(unittest.TestCase):
    """BIOLOGICAL_REASONING_CONSTITUTION.md Article XIV -- same input, same output, always."""

    def test_weakest_tier_is_deterministic_across_repeated_calls(self):
        inputs = ["established_evidence", "computational_prediction", "research_hypothesis"]
        results = [tp.weakest_tier(list(inputs)) for _ in range(100)]
        self.assertEqual(len({r.tier for r in results}), 1)
        self.assertEqual(len({r.reasoning for r in results}), 1)

    def test_confidence_propagation_is_deterministic_across_repeated_calls(self):
        inputs = ["numeric", "qualitative", None]
        results = [tp.propagate_confidence_type(list(inputs)) for _ in range(100)]
        self.assertEqual(len({r.confidence_type for r in results}), 1)
        self.assertEqual(len({r.reasoning for r in results}), 1)

    def test_module_has_no_io_or_randomness_imports(self):
        source = inspect.getsource(tp)
        import_lines = [
            line.strip() for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        for forbidden in ("random", "time", "datetime", "sqlite3", "urllib", "requests", "socket"):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(any(forbidden in line for line in import_lines))

    def test_module_has_no_gate_or_db_dependency(self):
        """006A is explicitly graph-free: it operates on plain values, not on the database."""
        source = inspect.getsource(tp)
        for forbidden in ("GRAPH.engine.gate", "GRAPH.engine.db", "import gate", "import db"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


class TestNotAnAIComponent(unittest.TestCase):
    """Structural proof of DOCS/MILESTONE_006_DESIGN.md's central scope boundary."""

    def test_no_hypothesis_generation_capability(self):
        public_names = [name for name in dir(tp) if not name.startswith("_")]
        forbidden_substrings = ("generate", "predict", "infer", "llm", "model_call")
        for name in public_names:
            lowered = name.lower()
            for forbidden in forbidden_substrings:
                with self.subTest(name=name, forbidden=forbidden):
                    self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
