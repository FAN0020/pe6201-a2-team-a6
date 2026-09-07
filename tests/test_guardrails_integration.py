"""D3 integration checks for guardrails in the complete scripted agent loop.

These tests deliberately exercise ``agent.run_case`` rather than calling the
Guardrails class directly.  Each test supplies a temporary scripted backend
case or configuration and restores all shared state before returning.
"""

import copy
import os
import sys
import unittest
from contextlib import contextmanager


SCAFFOLD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                        "A2_scaffold"))
if SCAFFOLD not in sys.path:
    sys.path.insert(0, SCAFFOLD)

import agent
import backends
import config
import tools


@contextmanager
def isolated_runtime(scripts=None, **config_overrides):
    """Temporarily change run_case inputs, restoring every shared object."""
    original_scripts = dict(backends.SCRIPTS)
    original_registry = {
        problem: dict(registry)
        for problem, registry in tools.REGISTRY.items()
    }
    original_config = {
        name: getattr(config, name)
        for name in ("BACKEND", "PROBLEM", "MAX_TURNS",
                     "MAX_TOKENS_PER_RUN", "AUTONOMY")
    }
    try:
        if scripts is not None:
            backends.SCRIPTS.update(copy.deepcopy(scripts))
        for name, value in config_overrides.items():
            setattr(config, name, value)
        yield
    finally:
        backends.SCRIPTS.clear()
        backends.SCRIPTS.update(original_scripts)
        tools.REGISTRY.clear()
        tools.REGISTRY.update(original_registry)
        for name, value in original_config.items():
            setattr(config, name, value)


def action_script(*calls):
    """Build a script whose calls each occupy a separate agent turn."""
    return [
        {"thought": "integration test action %d" % (index + 1),
         "calls": [call]}
        for index, call in enumerate(calls)
    ] + [{"final": {"decision": "test_complete"},
          "thought": "integration test conclusion"}]


class GuardrailsIntegrationTests(unittest.TestCase):
    """Verify that each D3 stop is observable through a full run_case."""

    def test_duplicate_action_stops_full_run_case(self):
        repeated = ("get_referral", {"referral_id": "REF-5602"})
        scripts = {"TEST-DUPLICATE": action_script(repeated, repeated)}
        with isolated_runtime(scripts, BACKEND="scripted", PROBLEM="B",
                              MAX_TURNS=8, MAX_TOKENS_PER_RUN=60000,
                              AUTONOMY="act"):
            record = agent.run_case("TEST-DUPLICATE", problem="B")

        self.assertEqual(record["stopped_by"], "duplicate_action")
        self.assertEqual(record["turns"], 2)
        self.assertEqual(record["evidence"], ["get_referral"])
        self.assertEqual(record["guardrails_fired"][-1]["guardrail"],
                         "duplicate_action")

    def test_step_cap_stops_full_run_case(self):
        scripts = {"TEST-STEP-CAP": action_script(
            ("get_referral", {"referral_id": "REF-5602"}),
            ("lookup_patient", {"patient_id": "P-1180"}),
        )}
        with isolated_runtime(scripts, BACKEND="scripted", PROBLEM="B",
                              MAX_TURNS=1, MAX_TOKENS_PER_RUN=60000,
                              AUTONOMY="act"):
            record = agent.run_case("TEST-STEP-CAP", problem="B")

        self.assertEqual(record["stopped_by"], "step_cap")
        self.assertEqual(record["turns"], 2)
        self.assertEqual(record["evidence"], ["get_referral"])
        self.assertEqual(record["guardrails_fired"][-1]["guardrail"],
                         "step_cap")

    def test_budget_ceiling_stops_full_run_case(self):
        scripts = {"TEST-BUDGET": action_script(
            ("get_referral", {"referral_id": "REF-5602"}),
            ("lookup_patient", {"patient_id": "P-1180"}),
        )}
        with isolated_runtime(scripts, BACKEND="scripted", PROBLEM="B",
                              MAX_TURNS=8, MAX_TOKENS_PER_RUN=4000,
                              AUTONOMY="act"):
            record = agent.run_case("TEST-BUDGET", problem="B")

        self.assertEqual(record["stopped_by"], "budget_ceiling")
        self.assertEqual(record["turns"], 1)
        self.assertEqual(record["evidence"], ["get_referral"])
        self.assertEqual(record["guardrails_fired"][-1]["guardrail"],
                         "budget_ceiling")

    def test_confirm_gate_holds_real_booking_before_book_slot(self):
        """The shipped multi-step booking flow must stop at its gate."""
        with isolated_runtime(BACKEND="scripted", PROBLEM="B",
                              MAX_TURNS=8, MAX_TOKENS_PER_RUN=60000,
                              AUTONOMY="confirm"):
            record = agent.run_case(
                "REF-5602", problem="B",
                approve=lambda action, payload: False)

        self.assertEqual(record["stopped_by"], "gate_held")
        self.assertNotIn("book_slot", record["evidence"])
        self.assertNotIn("book_slot",
                         [entry["tool"] for entry in record["tool_trace"]])
        self.assertEqual(record["guardrails_fired"][-1]["guardrail"],
                         "gate_held")


if __name__ == "__main__":
    unittest.main()
