#!/usr/bin/env python3
"""Compile the founder research folder into one cautious, source-linked plan.

Verdicts are MODEL POSITIVE, MODEL NEGATIVE, or INCOMPLETE. Even a positive
model is not proof of sales, market demand, or future profitability.
Synthetic panel responses never determine the verdict or sales forecasts.

python3 skills/founder-plan/compile.py --dir founder --check
python3 skills/founder-plan/compile.py --dir founder
"""

import argparse
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [
    ("summary.md", "Summary", "founder-plan"),
    ("board.md", "Concept review", "founder-board"),
    ("competitors.md", "Competitor evidence", "founder-competitors"),
    ("panel/results.md", "Synthetic objections exercise (not research)", "founder-consumer"),
    ("validation.md", "Real-world validation", "founder-validation"),
    ("pricing.md", "Pricing", "founder-pricing"),
    ("offer.md", "Offer", "founder-offer"),
    ("cfo.md", "Financial scenario", "founder-cfo"),
    ("marketing.md", "Marketing", "founder-marketing"),
    ("brand.md", "Brand", "founder-brand"),
    ("ops.md", "Operations", "founder-ops"),
    ("launch.md", "Launch or test", "founder-launch"),
]


def _load_unit_economics():
    path = os.path.join(HERE, "..", "founder-cfo", "unit_economics.py")
    ref = importlib.util.spec_from_file_location("founder_unit_economics", path)
    mod = importlib.util.module_from_spec(ref)
    ref.loader.exec_module(mod)
    return mod


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def _demote_h1(value):
    rows = value.splitlines()
    if rows and rows[0].startswith("# "):
        rows = rows[1:]
    return "\n".join("#" + row if row.startswith("#") else row for row in rows).strip()


def verdict(directory, min_buy_rate=None):
    """Return verdict, (pass, description) checks, scenario and synthetic panel.

    min_buy_rate is accepted for compatibility but never applied: synthetic
    willingness to buy is not validated purchasing behavior.
    """
    checks, model, panel = [], None, None
    raw = _read(os.path.join(directory, "numbers.json"))
    if raw:
        calculator = _load_unit_economics()
        try:
            model = calculator.analyse(json.loads(raw))
        except (ValueError, TypeError, calculator.NumbersError) as e:
            checks.append((False, "Financial input cannot be evaluated: %s" % e))
    else:
        checks.append((False, "Financial inputs not provided: founder/numbers.json"))
    if model:
        checks.extend([
            (model["contribution"] > 0, "Modeled contribution per placed %s: %.2f %s" % (
                model["unit"], model["contribution"], model["currency"])),
            (model["year1_profit"] > 0, "Modeled first-year operating result: %.2f %s" % (
                model["year1_profit"], model["currency"])),
        ])
        cap = model["capacity_per_month"]
        if cap is not None:
            checks.append((model["breakeven_per_month"] <= cap, "Monthly model break-even %.1f versus capacity %.1f" % (
                model["breakeven_per_month"], cap)))
            checks.append((model["plan_per_month"] <= cap, "Planned monthly orders %.1f versus capacity %.1f" % (
                model["plan_per_month"], cap)))
    panel_raw = _read(os.path.join(directory, "panel", "results.json"))
    if panel_raw:
        try:
            panel = json.loads(panel_raw)
        except json.JSONDecodeError:
            checks.append((False, "Synthetic panel file is not valid JSON"))
    if model is None:
        status = "INCOMPLETE"
    elif all(p for p, _ in checks):
        status = "MODEL POSITIVE (UNVALIDATED)"
    else:
        status = "MODEL NEGATIVE"
    return status, checks, model, panel


def compile_plan(directory, min_buy_rate=None):
    idea = _read(os.path.join(directory, "idea.md"))
    status, checks, model, panel = verdict(directory, min_buy_rate)
    title = (idea.splitlines()[0].lstrip("# ") if idea else None) or (
        model.get("business") if model else "Business concept")
    lines = ["# %s | Business decision dossier" % title, "",
             "**Scenario status: %s**" % status, "",
             "A favorable spreadsheet is not proof of profitability. Validate prices, costs, demand, and return rates with actual evidence.", ""]
    for passed, description in checks:
        lines.append("- %s %s" % ("PASS" if passed else "CHECK", description))
    if model:
        be = model["breakeven_per_month"]
        lines.extend(["", "## Financial scenario snapshot", "", "| Metric | Scenario result |",
                      "| --- | ---: |",
                      "| Currency | %s |" % model["currency"],
                      "| Gross unit price | %.2f |" % model["price"],
                      "| Net unit contribution after modeled refunds | %.2f |" % model["contribution"],
                      "| Planned orders per month | %.0f |" % model["plan_per_month"],
                      "| Break-even orders per month | %s |" % (
                          "not attainable" if math.isinf(be) else "%.1f" % be),
                      "| Modeled first-year operating result | %.2f |" % model["year1_profit"],
                      "| Model cumulative funding gap, excludes working capital | %.2f |" % model["cash_needed"],
                      ""])
    if panel:
        lines.extend(["## Synthetic panel (idea generation only)", "",
                      "This is simulated text, not a measured conversion rate. It did not affect the model status.",
                      "", "- Synthetic responses: %s" % panel.get("answered", "unknown"),
                      "- Recorded simulated 'buy' answers: %s" % panel.get("buys", "unknown"), ""])
    if idea:
        lines.extend(["## Concept", "", _demote_h1(idea), ""])
    absent = []
    for file, section, skill in SECTIONS:
        body = _read(os.path.join(directory, file))
        if body:
            lines.extend(["## " + section, "", _demote_h1(body), ""])
        else:
            absent.append((section, skill))
    if absent:
        lines.extend(["## Missing supporting sections", ""])
        lines.extend("- %s: use %s" % (name, skill) for name, skill in absent)
    lines.extend(["", "## Evidence status", "",
                  "Check founder/evidence.md and founder/validation.md for source URLs, supplier quotes,"
                  " actual orders, dated tests, refunds, and uncertain inputs.",
                  "If those records are absent, the business decision remains unverified.",
                  "Models exclude taxes, inventory/payment timing, and omitted cost categories.", ""])
    return status, "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder", help="folder containing idea.md and numbers.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--min-buy-rate", type=float, help="deprecated; ignored, synthetic rates never gate decisions")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.dir):
        print("error: no folder at %s" % args.dir, file=sys.stderr)
        return 2
    status, text = compile_plan(args.dir, args.min_buy_rate)
    if args.check:
        print("Status: " + status)
        for good, line in verdict(args.dir)[1]:
            print("  %s %s" % ("PASS" if good else "CHECK", line))
        return 1 if status != "MODEL POSITIVE (UNVALIDATED)" else 0
    filename = args.out or os.path.join(args.dir, "business-plan.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print("Status: %s. Wrote %s" % (status, filename))
    return 0


if __name__ == "__main__":
    sys.exit(main())
