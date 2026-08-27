# Aging-Chip RLS Pipeline

Human goal: convert longitudinal yeast aging-chip trap stacks into replicative-lifespan
measurements — per-trap division counts, on-chip death calls, and escape/censoring calls —
with a single human-annotation source of truth and a deployment-gated model workflow.

This project holds the canonical Python pipeline (annotator UI, trainer, diagnostics).
It is not for TIFF trap stacks, trained `.keras` models, the master annotation Excel,
or per-run reports; those live with the experiment data and deployment folder
(`C:\Users\jmccarthy\Desktop\Aging_chip_pipeline` and `Y:\Jordan\...`).

## Files

```text
projects/aging-chip-rls-pipeline/
  human_classifier_ui.py   OpenCV trap annotator: human labeling (single source of truth for
                           RLS ground truth AND frame labels), live AI overlay, calibrated
                           detector HUD (division / death / escape-censoring calls).
  train_classifier.py      Endpoint-trained multitask model (MobileNetV2 morphology + motion
                           branch): 7-class state head + direct division / dead / escape heads.
                           Calibrates decoders on held-out traps, evaluates on untouched test
                           traps, enforces a deployment gate (MAE, within-1, death agreement,
                           escape agreement); failed candidates export as candidate_* only.
  diagnose_classifier.py   Frame- and trap-level audit of a deployed or candidate model against
                           the master annotations (confusion, per-position error, RLS concordance).
```

## Canonical semantics (must not drift)

- Completed division: Late Bud -> Mother/Early Bud, bridging No Cell / Blurry gaps.
- Confirmed death: living state -> Dead Cell.
- "Mother Escaped (Ignore Rest)" censors the trap: divisions and death at/after the
  escape frame do not count. The model carries a dedicated escape head and a calibrated
  sustained-run censor decoder; the UI applies the identical rule at inference.
- `find_division_frames` / decode functions are ported verbatim between trainer and UI;
  do not edit one without the other.

## Version status (2026-08-27)

Escape/censoring retrofit trained on 116,657 annotation rows across three chips
(seed-42 trap-level split 207/42/42). Untouched-test: RLS MAE 3.07 (1.12 on escape-clean
traps), bias +0.17, death 85.7%, escape 85.7%. Deployment gate FAIL (automation withheld);
promoted as the assistive instrument on dominance over the escape-blind incumbent.
Details: `docs/handoffs/2026-08-27-aging-chip-rls-escape-retrofit-handoff.md`.
