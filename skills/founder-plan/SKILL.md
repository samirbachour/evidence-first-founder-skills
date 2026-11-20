---
name: founder-plan
description: Compile verified business evidence, unresolved questions, and the offline financial scenario into a decision dossier. Use for business plans and progress summaries; a positive projection is never described as validated profit.
---
# Decision dossier

Review all available project files: `founder/idea.md`, `evidence.md`, `validation.md`, `numbers.json`, and the other founder skill outputs. Do not fill missing material with fabricated copy. If the financial input is missing, do not forecast sales. If only synthetic panel answers exist, label them speculative and exclude them from financial decisions.

From the extracted root, run:

```bash
python3 skills/founder-plan/compile.py --dir founder --check
python3 skills/founder-plan/compile.py --dir founder
```

The script emits `MODEL POSITIVE (UNVALIDATED)`, `MODEL NEGATIVE` or `INCOMPLETE`. It does not claim empirical business profitability. It checks positive contribution and first-year modeled operating result and capacity (if supplied). It explicitly **ignores** artificial buy rates. The old `--min-buy-rate` parameter remains accepted for compatibility but has no effect.

Add a short human-edited summary based only on data provenance: decision, reason, confidence, top gap, lowest-cost validation action, accountable owner. If one unanswered fact is necessary for Step 1, stop at that dependency. Outputs: `founder/business-plan.md`, optionally `founder/one-pager.md` and `founder/summary.md`. Retain dates and sources with the plan.
