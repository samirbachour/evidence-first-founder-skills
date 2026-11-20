import json
import math
import unittest

from _load import load, example

ue = load("founder-cfo", "unit_economics")


def spec():
    with open(example("founder-cfo", "example.json"), encoding="utf-8") as f:
        return json.load(f)


class UnitEconomics(unittest.TestCase):
    def test_upstream_arithmetic_is_preserved(self):
        a = ue.analyse(spec())
        self.assertAlmostEqual(a["contribution"], 4.76, places=2)
        self.assertEqual(round(a["margin_at_plan"] * 100), 38)
        self.assertEqual(math.ceil(a["breakeven_per_day"]), 186)
        self.assertEqual(round(a["year1_profit"]), 93926)
        self.assertEqual(a["startup"], 25280)
        self.assertEqual(a["payback_month"], 8)
        self.assertEqual(round(a["cash_needed"]), 34092)
        self.assertEqual(a["flags"], [])

    def test_price_below_cost_is_flagged(self):
        s = spec()
        s["price"] = 1.5
        a = ue.analyse(s)
        self.assertTrue(math.isinf(a["breakeven_per_month"]))
        self.assertIn("non-positive", " ".join(a["flags"]))

    def test_capacity_and_plan_both_checked(self):
        s = spec()
        s["capacity_per_day"] = 150
        self.assertIn("capacity", " ".join(ue.analyse(s)["flags"]))
        s["capacity_per_day"] = 200
        self.assertIn("Planned volume exceeds", " ".join(ue.analyse(s)["flags"]))

    def test_monthly_orders_percent_fees_refunds(self):
        s = {"business": "Unverified scenario", "unit": "order", "price": 50,
             "variable": [{"label": "fulfillment", "cost": 17}],
             "variable_percent": [{"label": "payment", "rate": 0.03}],
             "refund_rate": 0.1, "refund_handling_per_order": 4,
             "fixed_monthly": [{"label": "hosting", "cost": 100}],
             "startup": [], "plan_per_month": 200, "ramp_per_month": [100] * 12}
        a = ue.analyse(s)
        self.assertEqual(a["volume_basis"], "monthly")
        self.assertAlmostEqual(a["net_revenue_per_unit"], 45)
        self.assertAlmostEqual(a["variable_per_unit"], 18.9)
        self.assertAlmostEqual(a["contribution"], 26.1)
        self.assertAlmostEqual(a["year1_profit"], (26.1 * 100 - 100) * 12)
        self.assertAlmostEqual(a["breakeven_per_month"], 100 / 26.1)
        # Fixed percentage fee recalculates against a changed price.
        cut = ue.analyse(s, price=40)
        self.assertAlmostEqual(cut["variable_per_unit"], 18.6)

    def test_sensitivity_moves_in_expected_direction(self):
        base = ue.analyse(spec())
        cheaper = ue.analyse(spec(), price=base["price"] * 0.9)
        fewer = ue.analyse(spec(), volume=0.8)
        self.assertLess(cheaper["year1_profit"], base["year1_profit"])
        self.assertLess(fewer["year1_profit"], base["year1_profit"])
        self.assertEqual(len(ue.sensitivity(spec())), 4)

    def test_bad_inputs_refused_no_guessed_costs(self):
        for mutation in (lambda s: s.pop("variable"),
                         lambda s: s.pop("variable_percent"),
                         lambda s: s.pop("refund_rate"),
                         lambda s: s.pop("ramp_per_day"),
                         lambda s: s.update(ramp_per_day=[100] * 11),
                         lambda s: s.update(price=0),
                         lambda s: s.update(refund_rate=1.2),
                         lambda s: s.update(variable_percent=[{"label": "fee", "rate": 2.9}]),
                         lambda s: s.update(days_per_month=0),
                         lambda s: s.update(plan_per_day=-1),
                         lambda s: s.update(price=float("nan"))):
            s = spec()
            mutation(s)
            with self.subTest(mutation=mutation):
                with self.assertRaises(ue.NumbersError):
                    ue.analyse(s)

    def test_report_labels_model_and_limitations(self):
        doc = ue.report(spec(), ue.analyse(spec()))
        for fragment in ("MODEL, NOT VERIFIED PROFIT", "CAD", "contribution per placed order", "model", "working capital"):
            self.assertIn(fragment.lower(), doc.lower())
        self.assertIn("93,926", doc)


if __name__ == "__main__":
    unittest.main()
