---
name: founder-consumer
description: Generate labeled fictional customer scenarios to explore objections and unclear value propositions. Use for qualitative brainstorming only, never demand measurement, predicted conversion, purchase forecasts or testimonials.
---
# Hypothetical objection exercise

The original skill ran 100 simulated buyers and reported a buy rate. This is **not statistically representative market research**. It is a creative stress test. Current research documents distortions in synthetic purchase intent and willingness-to-pay. See `research/RESEARCH_NOTES.md`.

Preferred manual workflow: use up to 8 to 12 distinct situations grounded in known real customer feedback and real product information. For each, identify: what a person might misunderstand, the strongest price/value objection, the unanswered trust question, and what an actual interview or checkout test would need to establish. Every item must be titled `MODEL-GENERATED HYPOTHESIS` and must not invent a demographic profile as an observed customer.

Optional historical bookkeeping utility: the bundled `panel.py` still produces separate persona prompts and tallies explicit answer files. It does **not** run a model itself or contact consumers. Default is 12 fictionally constructed scenarios, not 100. Use only with an agent environment that supports separate responses and explicit approval of computation cost. Do not use `buys`, `buy_rate`, or `purchases_first_month` as real metrics, a probability bound, or inputs to a financial plan.

Outputs: `founder/objections-hypotheses.md`; if the optional script is used, `founder/panel/` (explicitly synthetic). Actual reviews, interviews and purchase records belong in `founder/validation.md` via `founder-validation`.
