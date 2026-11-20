# Evidence-First Founder Skills

**14 reusable business-analysis skills for ChatGPT, Codex and compatible agent environments.** Includes four offline Python utilities for scenario calculations and report compilation.

This project adapts [Jake Schincariol's founder-skill](https://github.com/Jakeschincariol/founder-skill) under the [MIT license](LICENSE). The original copyright notice is retained. This independent derivative adds evidence safeguards, public-usable instructions, new skills and revised calculations. Neither the original author nor OpenAI or any named business figure endorses this adaptation.

## Why this exists

Business assistants can produce convincing plans from fictional customers, unstated costs and guessed sales volumes. This toolkit deliberately separates **observed facts**, **limited observations**, **explicit scenarios**, and **model-generated hypotheses**. A simulated customer panel is useful for finding potential objections; it is not evidence of buying behavior. A financially positive scenario is labeled `MODEL POSITIVE (UNVALIDATED)` until tested against real commercial evidence.

## Included skills

| Skill | Purpose |
| --- | --- |
| `founder-validation` | Evidence ledger, missing facts, real-customer validation |
| `founder-ecommerce` | Catalog and order audits using actual product and sales records |
| `founder-cfo` | Unit economics, monthly contribution and cash-flow scenarios |
| `founder-pricing` | Pricing investigation and price-sensitivity surveys |
| `founder-competitors` | Current-source competitive research |
| `founder-consumer` | Explicitly **fictional** objection brainstorming; not demand forecasts |
| `founder-offer` | Evidence-backed value propositions and offers |
| `founder-marketing` | Grounded campaign planning and compliant claims |
| `founder-brand` | Brand consistency and customer experience |
| `founder-ops` | Operating workflow and fulfillment dependencies |
| `founder-launch` | Controlled testing with predeclared success thresholds |
| `founder-board` | Business critique through three clearly attributed conceptual lenses |
| `founder-prioritize` | Compare opportunities without invented scores or revenues |
| `founder-plan` | Compile a decision dossier with explicit scenario status |

All skills are Markdown instructions under `skills/<name>/SKILL.md`. The Python utilities use the standard library and run only when executed in a Python-enabled environment; ChatGPT itself does not automatically run or install them.

## Use with ChatGPT Projects

1. Copy [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md) into a new or existing ChatGPT Project's instructions.
2. Add the `SKILL.md` files relevant to your work as Project files or paste the chosen skill into the conversation. Add your **actual** products, transactions and costs when asking for business-specific conclusions.
3. Example request: "Use founder-validation to identify missing evidence before examining the price, costs and conversion performance in the files I uploaded. Do not invent products or fill missing figures."

**Note:** Uploading this repository or a ZIP does **not automatically install a ChatGPT plugin**. Available integrations and Python execution differ by ChatGPT surface and account.

## Use with Codex and plugin-compatible agents

For repository-local Codex skill discovery, copy the desired skill directories to `.agents/skills/`, preserving each `SKILL.md` and its sibling scripts. This repository also contains a portable `plugin.json` manifest. Support for plugin installation and execution varies by agent and is **not verified** merely because the manifest parses. See the current [OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills) and [plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).

The core instructions are agent-independent. Other agent platforms may use their own skill discovery and permissions.

## Run the offline tools

Python 3.8+ and no third-party packages are required.

```bash
python3 -m unittest discover -s tests -v
python3 skills/founder-cfo/unit_economics.py path/to/numbers.json --out path/to/cfo.md
python3 skills/founder-pricing/van_westendorp.py path/to/human-survey.csv --source-type actual
python3 skills/founder-plan/compile.py --dir path/to/founder-folder
```

The unfilled [`templates/numbers-online-store.json`](templates/numbers-online-store.json) intentionally contains `null` placeholders. Replace required values with documented inputs or explicitly labeled hypothetical assumptions. The calculator rejects missing critical figures; a forecast is **not** proof of market demand, cash sufficiency or profitability.

## Structure

```text
plugin.json                    Portable plugin metadata
PROJECT_INSTRUCTIONS.md         Generic ChatGPT Project instructions
skills/                         14 skills including four offline Python utilities
research/RESEARCH_NOTES.md       Dated sources and methodological context
templates/                      Blank evidence, store, and financial inputs
tests/                          Local regression tests
CHANGELOG.md                    Summary of modifications
LICENSE                         MIT license and upstream copyright notice
```

## Licensing, credit, and limitations

Original project: [Jakeschincariol/founder-skill](https://github.com/Jakeschincariol/founder-skill), copyright (c) 2026 Jake Schincariol, MIT. This project is an independently maintained derivative, not an official fork or endorsed package. The author names and book titles in the research notes are citations, not endorsements or simulated advisors.

The code reads local input files and writes user-directed local output files. It does **not** connect to stores, advertising platforms, payment processors or other accounts on its own. Evaluate outputs against current original sources; actual business outcomes can differ substantially from scenarios. Do not upload access tokens, private customer information or bank records to a public repository.
