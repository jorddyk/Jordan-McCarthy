# 2026-08-27 Code Handoff — Aging-Chip RLS Pipeline Escape/Censoring Retrofit

## Repo

`jorddyk/Jordan-McCarthy`

## Scope

First import of the canonical aging-chip RLS pipeline into the code vault, at the
escape/censoring-retrofit revision, into a new project folder
`projects/aging-chip-rls-pipeline/` (the ImageJ/Fiji project is macros-only by charter).

## What changed in the code (vs. the previous, un-vaulted revision)

- "Mother Escaped (Ignore Rest)" promoted from excluded annotation to 7th trainable
  state class; post-escape frames retained as supervision instead of being trimmed.
- Detector gained a dedicated escape sigmoid head (3-output export: division/dead/escape)
  plus a calibrated sustained-run censor decoder written to `rls_detector_meta.json`.
- Evaluation made honest: full post-escape frame tails included; concordance CSV reports
  per-trap true/pred escape flags and frames; deployment gate extended with
  escape-call agreement >= 90%.
- Annotator UI decodes the censor live ("escaped @ f=K (censored)"); backward compatible
  with legacy 2-output detectors.

## Motivation

Live use showed runaway division counting on escaped-mother traps (e.g., human 26 vs
detector 50), concentrated in the CR x Mud1-delete arm (Pos41, 26% escape rate) — a
condition-correlated censoring bias. Root cause: training and all prior metrics lived in
an escape-sanitized world (post-escape rows trimmed before loading).

## Result of the retrained candidate (untouched test, n=42 traps)

MAE 3.07 / bias +0.17 / within-1 59.5% / death 85.7% / escape 85.7% -> GATE FAIL
(automation withheld). Escape-clean traps: MAE 1.12 / within-1 69% / exact 50%.
Promoted as assistive instrument 2026-08-27; five production artifacts replaced as a set
with timestamped `pre_escape_*` backups; six-condition-chip interaction arms show no
material signed bias in this sample (Pos21 +0.4, Pos31 -0.5, Pos41 0.0).

## Explicit exclusions per repo hard rules

No `.keras` models, no `master_human_annotations.xlsx`, no TIFF stacks, no per-run
CSV/JSON reports. Code + this record only.

## Follow-ups

- Escape censor-frame placement (median error 39.5 frames) is the weakest joint;
  new escaped-trap annotations directly improve it.
- Pos51 (Mud1-intronless x 0.1% glucose) has zero annotations.
- Corresponding intelligence memo filed in Drive:
  "HEARTH UPDATE — RLS Tracker escape-censoring retrofit and assistive promotion — 27 Aug 2026".
