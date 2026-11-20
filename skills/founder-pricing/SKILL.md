---
name: founder-pricing
description: Analyze actual product prices, competitor comparables, real survey responses and contribution margins. Use for price or discount decisions. Do not use simulated willingness-to-pay as validated evidence.
---
# Pricing and discount tests

Read exact current catalog or offer, channel prices, shipping charges, supplier costs and the most recent real competitor comparables. If these are missing, identify the missing export/URL before recommending a price. If the owner asks for a planning scenario, label it and show sensitivity only.

The bundled `van_westendorp.py` plots four survey price anchors. Valid use starts from **actual** human responses, with declared study conditions and representative-sample caveats. The command `python skills/founder-pricing/van_westendorp.py prices.csv --source-type actual --out founder/pricing-curve.md` calculates descriptive intersections for respondents; it does not compute the revenue-maximizing price. For artificial responses, use `--source-type synthetic` and never present the curve as empirical demand. Unspecified source defaults to **unverified**.

For apparel, evaluate original item price and paid discount separately; keep product, size, shipping treatment, bundle quantities and promotions comparable. Calculate net contribution after manufacturing, shipping subsidies, refunds, percentage-based transaction fees and acquisition costs. Verify actual current prices from WooCommerce or published product pages. The true maximum sustainable customer acquisition cost depends on observed gross margin, measured repeat purchases, the refund rate and required cash buffer, not invented lifetime value.

Output `founder/pricing.md`, with a dated comparison, verified price/cost sources, assumptions, and a real controlled test proposal. Never invent an inflated "previous price", guaranteed results, or a deadline.
