# Rongorongo decipherment

Human goal: computational cryptanalysis / statistical hypothesis testing of the Rongorongo script (undeciphered Rapa Nui writing system), run as blind/adversarial preregistered tests rather than pattern-matching for a desired answer.

This is a distinct research track from JM105/Intronsaurus. Prior sealed blind-test runs for this project exist as isolated, non-merged branches used only to execute a preregistered test in a clean CI environment (see `rr/f6r1-jm-a1-sealed`, `rongorongo-y20f-sealed`, `rongorongo-phase19-temp`) — those branches intentionally stay unmerged; their durable results are transferred to the Rongorongo Drive ledger, not kept as long-lived git history. This directory is different: it preserves reusable, complete, currently-accessible **reproduction/validation code**, not sealed-test scaffolding.

## Repository map

```text
projects/rongorongo/
  omega-swarm-reproduction/
    Purpose: reproduce the frozen-corpus statistical tests (Ba6 exact anti-adjacency,
    terminal-core Monte Carlo, two-part compound mirror/orientation tests) behind the
    2026-07-17 OMEGA-SWARM adjudication runs. Verdict of every run reproduced here:
    "NO SYSTEM SURVIVED" (no decipherment candidate cleared the preregistered gates).
  prometheus-null-compiler/
    Purpose: fail-closed Rongorongo <-> Old Rapa Nui "compiler" that deliberately
    refuses to decode/encode, because the authoritative sign-value ledger has zero
    promoted values. Exposes only independently-supported structure (token equality
    classes, repeated spans, compound-attachment geometry).
  hrfa-validator/
    Purpose: leakage-checking validator/anonymizer for a blinded structural-formula
    coding scheme (HRF001-HRF032) used to code narrative/formulaic structure without
    smuggling in historical/collector metadata that could bias blind judges.
```

## Validation performed by this import

- All Python files pass `python -m py_compile`.
- `prometheus-null-compiler/rr_prometheus_compiler.py self-test` was actually executed and its output matches the self-test result recorded in the source Drive document exactly (`{"status": "PASS", "tests": 4, ...}`).
- The Ba6 exact-probability arithmetic (`math.comb(17,11) / math.comb(27,11) = 0.0009492329858462582`) embedded in two of the scripts was independently recomputed and matches.
- Files were extracted from Google Drive via plain-text/base64 export (not the default markdown-converted view) specifically to avoid markdown-escaping corruption of code (`<`, `>`, `#!`, `__`, etc.). Extraction was spot-checked against the source documents.

## What is NOT included, and why

Several companion data/support files that these scripts import or open at runtime were referenced by name and SHA-256 hash in the source Drive documents but were **not themselves found** anywhere in Drive (only their hashes were recorded, not their bytes):

- `horley_encoding.py`, `horley_parallels.csv`, `frozen_passages.json` (used by `omega-swarm-reproduction/reproduce_structural_tests.py`)
- `passage_atlas_frozen.csv` (used by `omega-swarm-reproduction/omega_reproduce.py`)
- `RR_SEALED_IDENTITY__actor-KoruAtlas-GPT56T-Sigma__20260716T164620+0200__run-PA3-2C91` Excel workbook (used by `omega-swarm-reproduction/01_reproduce_tournament.py`)
- `input_manifest_OMEGA-SWARM-F303E582.json`, `systems_OMEGA-SWARM-F303E582.csv` (used by `omega-swarm-reproduction/reproduce_adjudication_omega_swarm_f303e582.py`)
- `formula_atlas.jsonl` (used by `hrfa-validator/rr_hrfa_validator.py`)

Per this repository's rule that filenames/hashes are recovery clues and not recovered runnable source, these companion files are **not** fabricated or reconstructed here. Each script directory's own README states this per-script. The **code itself** is complete, exact, and verified (see above) — only the frozen input data it operates on is outside Drive's reach (most likely local machine or a private downloadable "reproduction ZIP" referenced repeatedly in the source docs but not directly accessible to this automation).

Two Drive folders that were not deep-searched by this pass and may contain the missing companion files: "Rongorongo Decipherment" (id `1kcOu4vkaudFu7mWBS3efGT_HWfI1ngs2`) and "TAU_RONGORONGO_REPLICATION_PREP_2" (id `1PNj62Q3schlCmgigaJlpNJi0YGoSx4EY`).

## Hard rules (inherited from repository root)

- No sign value, phonetic reading, or grammatical claim is treated as established. Every script here defaults to the null/no-decipherment position (`NO SYSTEM SURVIVED`, `UNSUPPORTED`, confidence 0.0) unless a preregistered gate is explicitly met.
- Do not silently "fill in" or reconstruct missing companion data files — mark them missing (as above) instead.
- Sealed/blind-test workflows for Rongorongo belong in short-lived, non-merged branches (existing convention), not in this project directory.
