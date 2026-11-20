---
name: founder-cfo
description: Compute sourced monthly unit contribution, refund-adjusted revenue, break-even, operating scenarios and funding gaps with the bundled offline Python calculator. Use only when the user supplies prices, costs and a sales scenario.
---
# Financial scenario, not proof of profit

**First verify the data.** For stores, use actual order exports and current production/shipping costs. Identify exact currency, gross unit price, expected refunds, production/fulfilment, buyer-paid shipping, seller-funded shipping, payment percentage and flat charges, packaging, advertising, discounting, subscriptions, customer support, and fixed costs. Do not assume zero when a cost category is unknown; explicitly mark missing fields before running. For service businesses include owner time and labor where applicable.

Populate a private per-project `founder/numbers.json` using the example or `templates/numbers-online-store.json`. The offline script needs explicit `variable`, `variable_percent` (use an empty list only if percentage-based charges are already covered or truly absent), `refund_rate`, `fixed_monthly`, `startup`, and 12 monthly sales numbers in `ramp_per_month` (or 12 daily forecasts in `ramp_per_day`). It supports `variable_percent`, `refund_rate`, and `refund_handling_per_order`; amounts are before tax. Sources and unverifiable projections go in `founder/evidence.md`.

Run in the extracted toolkit root:

```bash
python3 skills/founder-cfo/unit_economics.py founder/numbers.json --out founder/cfo.md
python3 skills/founder-cfo/unit_economics.py founder/numbers.json --json
```

The second command prints machine-readable model output. If the skill is installed elsewhere, run the script in the same folder as this SKILL.md. Report what inputs are actual and what are projections; distinguish fixed costs, per-order contribution and modeled operating margin. The calculated funding gap omits working capital, payout delays, taxes, and finance charges. Never call a positive scenario "actual profit". Output `founder/numbers.json`, `founder/cfo.md`, `founder/evidence.md`.
