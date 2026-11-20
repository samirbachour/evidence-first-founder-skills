#!/usr/bin/env python3
"""Offline, evidence-aware business scenario calculator (standard library only).

Calculates a twelve-month operating scenario. This does NOT predict sales,
verify inputs, compute accounting profit/tax, or model working-capital timing.

Input is JSON. See templates/numbers-online-store.json and
skills/founder-cfo/example.json for the supported daily and monthly formats.

Example:
  python3 skills/founder-cfo/unit_economics.py founder/numbers.json --out founder/cfo.md
  python3 skills/founder-cfo/unit_economics.py founder/numbers.json --json

Mandatory: price, variable (list), variable_percent (list, even if empty),
refund_rate, fixed_monthly (list), startup (list), and an explicit 12-month ramp (ramp_per_month OR ramp_per_day). No assumed sales.
variable_percent rates use decimal fractions such as 0.029 for 2.9% of gross
price; refund_rate is the explicitly declared fraction of fully refunded orders.
Optional: refund_handling_per_order (cost per refunded order), and capacity_per_month/day.
All units are orders (including ultimately refunded orders); no partially
refunded or multiple-item order model. Model these externally if material.
"""

import argparse
import json
import math
import sys


class NumbersError(Exception):
    pass


def _num(v, label, minimum=0, positive=False):
    if isinstance(v, bool):
        raise NumbersError("%s must be a number, not a boolean" % label)
    try:
        x = float(v)
    except (TypeError, ValueError):
        raise NumbersError("%s must be numeric" % label)
    if not math.isfinite(x) or x < minimum or (positive and x == 0):
        raise NumbersError("%s must be a finite %snumber >= %s" % (
            label, "positive " if positive else "", minimum))
    return x


def _sum(items, field):
    if not isinstance(items, list):
        raise NumbersError("'%s' must be explicitly supplied as a list (use [] if truly zero)" % field)
    total = 0.0
    for idx, it in enumerate(items):
        if not isinstance(it, dict) or not it.get("label") or "cost" not in it:
            raise NumbersError("%s[%d] requires a label and cost" % (field, idx))
        total += _num(it["cost"], "%s[%d].cost" % (field, idx))
    return total


def _rates(items):
    if not isinstance(items, list):
        raise NumbersError("variable_percent must be a list")
    total = 0.0
    for idx, it in enumerate(items):
        if not isinstance(it, dict) or not it.get("label") or "rate" not in it:
            raise NumbersError("variable_percent[%d] requires a label and rate" % idx)
        rate = _num(it["rate"], "variable_percent[%d].rate" % idx)
        if rate > 1:
            raise NumbersError("rates are decimal fractions: use 0.029 for 2.9%, not 2.9")
        total += rate
    if total > 1:
        raise NumbersError("percentage-based variable costs exceed 100% of gross price")
    return total


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            obj = json.load(fh)
    except (FileNotFoundError, OSError) as e:
        raise NumbersError("cannot read %s: %s" % (path, e))
    except json.JSONDecodeError as e:
        raise NumbersError("invalid JSON: %s" % e)
    if not isinstance(obj, dict):
        raise NumbersError("input must be a JSON object")
    return obj


def analyse(spec, price=None, volume=1.0):
    """Pure function. Model every specified order, including refunded orders."""
    if not isinstance(spec, dict):
        raise NumbersError("input must be an object")
    p = _num(price if price is not None else spec.get("price"), "price", positive=True)
    scale = _num(volume, "volume", positive=True)
    days = _num(spec.get("days_per_month", 30), "days_per_month", positive=True)
    fixed = _sum(spec.get("fixed_monthly"), "fixed_monthly")
    startup = _sum(spec.get("startup"), "startup")
    base_var = _sum(spec.get("variable"), "variable")
    percent_total = _rates(spec.get("variable_percent"))
    refund_rate = _num(spec.get("refund_rate"), "refund_rate")
    if refund_rate > 1:
        raise NumbersError("refund_rate must be 0 to 1")
    refund_handling = _num(spec.get("refund_handling_per_order", 0), "refund_handling_per_order")
    if "ramp_per_day" in spec and "ramp_per_month" in spec:
        raise NumbersError("use either monthly or daily ramp, not both")
    monthly = "ramp_per_month" in spec
    ramp_key = "ramp_per_month" if monthly else "ramp_per_day"
    plan_key = "plan_per_month" if monthly else "plan_per_day"
    cap_key = "capacity_per_month" if monthly else "capacity_per_day"
    if ramp_key not in spec:
        raise NumbersError("an explicit 12-number ramp_per_month or ramp_per_day is required")
    if (monthly and any(k in spec for k in ("plan_per_day", "capacity_per_day"))) or (
        not monthly and any(k in spec for k in ("plan_per_month", "capacity_per_month"))
    ):
        raise NumbersError("daily and monthly volume formats cannot be mixed")
    ramp = spec[ramp_key]
    if not isinstance(ramp, list) or len(ramp) != 12:
        raise NumbersError("%s requires exactly 12 monthly volume entries" % ramp_key)
    ramp = [_num(v, "%s[%d]" % (ramp_key, i)) * scale for i, v in enumerate(ramp)]
    plan = _num(spec.get(plan_key, ramp[-1]), plan_key) * scale
    if plan == 0:
        raise NumbersError("plan volume must be above zero")
    cap = None if cap_key not in spec else _num(spec[cap_key], cap_key, positive=True)
    unit_revenue = p * (1 - refund_rate)
    var = base_var + p * percent_total + refund_rate * refund_handling
    contribution = unit_revenue - var
    be_month = math.inf if contribution <= 0 else fixed / contribution
    plan_units_month = plan if monthly else plan * days
    profit_plan = contribution * plan_units_month - fixed
    planned_revenue = unit_revenue * plan_units_month
    margin_at_plan = profit_plan / planned_revenue if planned_revenue else float("-inf")

    months, cumulative, payback = [], -startup, None
    for idx, raw in enumerate(ramp, start=1):
        units = raw if monthly else raw * days
        gross_sales = units * p
        refunds = units * p * refund_rate
        recognized_revenue = gross_sales - refunds
        variable_cost = units * var
        profit = recognized_revenue - variable_cost - fixed
        cumulative += profit
        if payback is None and cumulative >= 0:
            payback = idx
        months.append({
            "month": idx, "volume": raw, "units": units, "gross_sales": gross_sales,
            "refunds": refunds, "revenue": recognized_revenue,
            "variable": variable_cost, "fixed": fixed, "profit": profit,
            "cumulative": cumulative,
        })
    year_profit = sum(m["profit"] for m in months)
    year_revenue = sum(m["revenue"] for m in months)
    cash_gap = -min([-startup] + [m["cumulative"] for m in months])
    flags = []
    if contribution <= 0:
        flags.append("Each placed order has non-positive modeled contribution.")
    capacity_month = cap if monthly else (None if cap is None else cap * days)
    if capacity_month is not None and be_month > capacity_month:
        flags.append("Modeled break-even exceeds stated capacity.")
    if capacity_month is not None and plan_units_month > capacity_month:
        flags.append("Planned volume exceeds stated capacity.")
    if year_profit <= 0:
        flags.append("Year 1 operating model is not profitable at the supplied sales ramp.")
    if payback is None:
        flags.append("The modeled startup expenditure is not recovered within 12 months.")
    return {
        "business": spec.get("business", ""), "unit": spec.get("unit", "order"),
        "currency": spec.get("currency", "USD"), "volume_basis": "monthly" if monthly else "daily",
        "price": p, "net_revenue_per_unit": unit_revenue, "refund_rate": refund_rate,
        "refund_handling_per_order": refund_handling,
        "variable_base_per_unit": base_var, "variable_percent_rate": percent_total,
        "variable_per_unit": var, "contribution": contribution,
        "contribution_pct": contribution / p, "fixed_monthly": fixed, "startup": startup,
        "plan_per_day": plan / days if monthly else plan,
        "plan_per_month": plan if monthly else plan * days,
        "margin_at_plan": margin_at_plan,
        "breakeven_per_month": be_month,
        "breakeven_per_day": be_month / days,
        "capacity_per_day": cap / days if monthly and cap is not None else cap,
        "capacity_per_month": capacity_month,
        "year1_revenue": year_revenue, "year1_profit": year_profit,
        "year1_after_startup": year_profit - startup,
        "payback_month": payback, "cash_needed": cash_gap,
        "months": months, "flags": flags,
        "variable_items": spec["variable"], "percent_items": spec["variable_percent"],
        "fixed_items": spec["fixed_monthly"], "startup_items": spec["startup"],
    }


def sensitivity(spec):
    base = analyse(spec)
    variants = [("Base scenario", base), ("Price -10%", analyse(spec, price=base["price"] * 0.9)),
                ("Volume -20%", analyse(spec, volume=0.8))]
    worse = json.loads(json.dumps(spec))
    for it in worse["variable"]:
        it["cost"] = float(it["cost"]) * 1.15
    variants.append(("Per-order fixed-amount costs +15%", analyse(worse)))
    return variants


def _money(value, currency="USD", decimals=2):
    if math.isinf(value):
        return "not reachable"
    if math.isnan(value):
        return "not available"
    symbol = "$" if currency == "USD" else currency + " "
    sign = "-" if value < 0 else ""
    return "%s%s%s" % (sign, symbol, format(abs(value), ",.%df" % decimals))


def report(spec, a):
    fmt = lambda v, decimals=2: _money(v, a["currency"], decimals)
    unit = a["unit"]
    lines = ["# Operating scenario: %s" % (a["business"] or "Unnamed business"), "",
             "**MODEL, NOT VERIFIED PROFIT.** Results depend on supplied volume, refunds, prices and cost inputs.",
             "Currency: %s. Forecast period: 12 equal-length model months; taxes and working-capital timing are excluded." % a["currency"], "",
             "## Economics per placed %s" % unit, "", "| Component | Amount |", "| --- | ---: |",
             "| Price before refund | %s |" % fmt(a["price"]),
             "| Expected refunds on this order | -%s |" % fmt(a["price"] * a["refund_rate"]),
             "| Retained revenue per order | %s |" % fmt(a["net_revenue_per_unit"])]
    for it in a["variable_items"]:
        lines.append("| %s | -%s |" % (it["label"], fmt(float(it["cost"]))))
    for it in a["percent_items"]:
        lines.append("| %s (%.2f%% of gross price) | -%s |" % (
            it["label"], 100 * float(it["rate"]), fmt(float(it["rate"]) * a["price"])))
    if a["refund_handling_per_order"]:
        lines.append("| Expected refund handling | -%s |" % fmt(a["refund_handling_per_order"] * a["refund_rate"]))
    lines.extend(["| **Contribution per placed order** | **%s** |" % fmt(a["contribution"]), "",
                  "## Monthly operating scenario", "",
                  "- Fixed monthly costs: %s" % fmt(a["fixed_monthly"]),
                  "- Planned volume: %.0f orders per month" % a["plan_per_month"],
                  "- Break-even: %s orders per month" % (
                      "not reachable" if math.isinf(a["breakeven_per_month"]) else "%.1f" % a["breakeven_per_month"]),
                  "- Modeled operating margin at plan: %s" % (
                      "n/a" if math.isinf(a["margin_at_plan"]) else "%.1f%%" % (a["margin_at_plan"] * 100)),
                  "", "| Month | Placed orders | Retained revenue | Operating result | Model cumulative after startup |",
                  "| ---: | ---: | ---: | ---: | ---: |"])
    for m in a["months"]:
        lines.append("| %d | %.0f | %s | %s | %s |" % (
            m["month"], m["units"], fmt(m["revenue"], 0), fmt(m["profit"], 0), fmt(m["cumulative"], 0)))
    lines.extend(["", "- Year 1 modeled retained revenue: %s" % fmt(a["year1_revenue"], 0),
                  "- Year 1 modeled operating result: %s" % fmt(a["year1_profit"], 0),
                  "- Model cumulative funding gap (excludes working capital and payment timing): %s" % fmt(a["cash_needed"], 0),
                  "- Startup expenditure recovered in model: %s" % (
                      "month %s" % a["payback_month"] if a["payback_month"] else "not within first 12 model months"),
                  "", "## Sensitivity", "",
                  "| Model | Contribution per order | Break-even orders/month | Year 1 result |",
                  "| --- | ---: | ---: | ---: |"])
    for name, scenario in sensitivity(spec):
        lines.append("| %s | %s | %s | %s |" % (
            name, fmt(scenario["contribution"]),
            "not reachable" if math.isinf(scenario["breakeven_per_month"]) else "%.1f" % scenario["breakeven_per_month"],
            fmt(scenario["year1_profit"], 0)))
    if a["flags"]:
        lines.extend(["", "## Model cautions", ""] + ["- " + f for f in a["flags"]])
    lines.extend(["", "## Limitations", "",
                  "This is a contribution and operating-cost scenario, not a cash flow statement or audited profit.",
                  "It does not automatically include taxes, inventory timing, advertising, owner compensation,"
                  " chargebacks, fraud, discounts, or other costs unless explicitly entered above.",
                  "Inputs must be linked to actual exports, quotes, invoices, or clearly labelled scenarios."])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("numbers", help="JSON financial scenario inputs")
    parser.add_argument("--price", type=float, help="what-if gross order price")
    parser.add_argument("--volume", type=float, default=1, help="what-if volume multiplier")
    parser.add_argument("--out", help="write Markdown report")
    parser.add_argument("--json", action="store_true", help="print machine-readable scenario")
    args = parser.parse_args(argv)
    try:
        spec = load(args.numbers)
        if args.price is not None:
            spec = dict(spec, price=args.price)
        if args.volume != 1:
            spec = dict(spec)
            for key in ("plan_per_day", "plan_per_month"):
                if key in spec:
                    spec[key] = float(spec[key]) * args.volume
            for key in ("ramp_per_day", "ramp_per_month"):
                if key in spec:
                    spec[key] = [float(v) * args.volume for v in spec[key]]
        model = analyse(spec)
    except NumbersError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if args.json:
        payload = {k: v for k, v in model.items() if not k.endswith("_items")}
        for k, v in list(payload.items()):
            if isinstance(v, float) and not math.isfinite(v):
                payload[k] = None
        print(json.dumps(payload, indent=2, allow_nan=False))
        return 0
    result = report(spec, model)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(result)
        print("Wrote %s" % args.out)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
