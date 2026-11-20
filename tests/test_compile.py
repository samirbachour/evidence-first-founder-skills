import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

plan = load("founder-plan", "compile")


class Compile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "idea.md"), "w") as f:
            f.write("# Example only\n\nUnverified business concept.\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def numbers(self, **changes):
        with open(example("founder-cfo", "example.json")) as f:
            spec = json.load(f)
        spec.update(changes)
        with open(os.path.join(self.d, "numbers.json"), "w") as f:
            json.dump(spec, f)

    def panel(self, buys):
        os.makedirs(os.path.join(self.d, "panel"), exist_ok=True)
        with open(os.path.join(self.d, "panel", "results.json"), "w") as f:
            json.dump({"buys": buys, "passes": 100 - buys, "answered": 100,
                       "buy_rate": buys / 100, "evidence_type": "synthetic"}, f)

    def test_missing_numbers_incomplete(self):
        status, content = plan.compile_plan(self.d)
        self.assertEqual(status, "INCOMPLETE")
        self.assertIn("not provided", content)

    def test_favorable_scenario_is_unvalidated(self):
        self.numbers()
        self.panel(100)
        status, content = plan.compile_plan(self.d)
        self.assertEqual(status, "MODEL POSITIVE (UNVALIDATED)")
        self.assertIn("not proof", content)
        self.assertIn("simulated text", content.lower())
        self.assertNotIn("**Verdict: Profitable**", content)

    def test_synthetic_buy_rate_can_never_change_verdict(self):
        self.numbers()
        self.panel(1)
        low = plan.compile_plan(self.d)[0]
        self.panel(99)
        high = plan.compile_plan(self.d)[0]
        self.assertEqual(low, high)
        self.assertEqual(low, "MODEL POSITIVE (UNVALIDATED)")
        self.assertEqual(plan.verdict(self.d, min_buy_rate=1.0)[0], low)

    def test_losing_scenario_negative(self):
        self.numbers(price=3)
        self.assertEqual(plan.compile_plan(self.d)[0], "MODEL NEGATIVE")

    def test_capacity_block_negative(self):
        self.numbers(capacity_per_day=50)
        self.assertEqual(plan.compile_plan(self.d)[0], "MODEL NEGATIVE")

    def test_malformed_numbers_incomplete(self):
        self.numbers(ramp_per_day=[1] * 11)
        self.assertEqual(plan.compile_plan(self.d)[0], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
