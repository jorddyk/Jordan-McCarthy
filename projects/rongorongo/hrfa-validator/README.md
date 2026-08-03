# HRFA formula-atlas validator/anonymizer

Recovered verbatim from Drive file "RR_HRFA__VALIDATOR__actor-Kaihu-SourceCritic-GPT56T__20260716T165717+0200__run-HRFA-A7C9.py" (id `1IfHlwm_b8ZZpglemdokqan4d8nmQ-4sC`, native `text/x-python` file — not a Google Doc — created/modified 2026-07-16).

## What it does

Reads `formula_atlas.jsonl` (one JSON record per narrative/formulaic structure family, keyed by `family_id` `HRF001`-`HRF032`) and writes `anonymous_structures.regenerated.csv`. Each family's slot order, length distribution, omission/expansion/reset behavior, and refrain subtype are hard-coded lookup tables in this script (not read from the atlas), so the atlas only supplies per-record counts and scores.

Before writing output it enforces two blind-coding guardrails and hard-fails (`SystemExit`) if either is violated:

- `BANNED_HEADERS` — output columns must never be named things like `source_url`, `collector`, `informant`, `translation`, etc. (would leak identifying/interpretive metadata into what is meant to be a blinded structural dataset).
- `BANNED_TERMS` — output cell values must never contain interpretive/historical terms (`routledge`, `thomson`, `métraux`, `rapa nui`, `genealogy`, `calendar`, `ritual`, `royal`, `migration`, `birdman`, `chant`, ...), checked with word-boundary regex across every row.

It also requires every output row's `falsifier_status_code` to equal `FALSIFIER_PRESENT`, i.e. every coded structure must carry an explicit falsification condition — rows without one abort the run.

## Status: RECOVERED — code complete, input not located

`python -m py_compile` passes. The file itself is a real, complete, native `.py` file (not reconstructed from a doc mirror), so there is no markdown-escaping risk here. It is not runnable in this repository because its input, `formula_atlas.jsonl` (one line per `HRF001`-`HRF032` family with fields like `entry_count`, `clause_count`, `specificity_score_1_10`, `prediction_risk_1_10`, `refrain_subtype`), was not located anywhere in Drive — only this validator script was found.
