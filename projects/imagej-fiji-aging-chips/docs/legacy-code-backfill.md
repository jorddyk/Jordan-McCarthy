# ImageJ / Fiji Aging-Chip Legacy Code Backfill

_Last updated: 2026-07-12 Europe/Zurich_

Purpose: track exact-source recovery for historical JM076/JM128/JM129 Fiji macros and Groovy scripts. This file is a recovery ledger, not runnable code.

## Recovery standard

A script is recovered only when its complete source body is available and can be inspected as a runnable `.ijm` macro, Groovy script, or intentionally documented template. Filenames, output names, dimension metadata, protocol summaries, and remembered logic are recovery clues only.

## Current priority queue

| Priority | Proposed human filename | Source clues | Status |
|---|---|---|---|
| 1 | `macros/jm128-split-nd2-positions-bioformats.ijm` | `Image001.nd2`; `Image001_Pos0_Hyperstack.tif`; Bio-Formats Macro Extensions; `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions` | `exact full source not yet recovered` |
| 2 | `macros/jm128-extract-mitosox-c2-every6-zpositions.ijm` | `C=2`; `Z=60`; `T=107`; frames `1,7,13...`; `MitoSOX_only_C2_T1_every6_Zpositions` | `exact full source not yet recovered` |
| 3 | `macros/jm128-stitch-image-and-image001-brightfield-rls.ijm` | `Image.nd2`; `Image001.nd2`; 30 positions; `1024x1022`; `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif` | `exact full source not yet recovered` |
| 4 | `macros/jm128-merge-ros-bf-fl.ijm` | `PosX_BF.tif`; `PosX_FL.tif`; `outputOffset = 1`; `firstSourcePos = 0`; `lastSourcePos = 29`; `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif` | `exact full source not yet recovered` |
| 5 | `groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy` | `MitosoxRedInducibleFusionsRepeat.nd2`; `Continue001.nd2`; `Continue002.nd2`; `rollingBallRadius=100`; `C=2`; `Z=60`; `T=107/139/145`; global ranges `1-107`, `108-246`, `247-391` | `exact full source not yet recovered` |
| 6 | `macros/jm076-detect-adjust-convert-resize.ijm` | `Y:/Jordan/JM076/Macros/Step1_DetectAdjustConvertResize.ijm` | `exact full source not yet recovered` |
| 7 | `macros/jm076-brightfield-extractor.ijm` | `Y:/Jordan/JM076/Macros/Step2_BriightfieldExtractor.ijm` | `exact full source not yet recovered` |
| 8 | `macros/jm076-convert-resize.ijm` | `Y:/Jordan/JM076/Macros/Step_3ConvertResize.ijm` | `exact full source not yet recovered` |
| 9 | `macros/jm076-remove-brightfield-slices-from-stack.ijm` | `Y:/Jordan/JM076/Macros/Step4_RemovebrightfieldSlicesFromStack.ijm` | `exact full source not yet recovered` |
| 10 | `macros/jm076-red-channel-extractor.ijm` | `Y:/Jordan/JM076/Macros/Step6_RedChannelMacro.ijm` | `exact full source not yet recovered` |

## Recovery pass: 2026-08-08

Three Google Docs (created/modified 2026-08-06/07, all after the last repository commit `3db310b` of 2026-07-28) describe a substantial new system, the **Yeast Cell Replicative Lifespan (RLS) Tracker & AI Engine**, proposed as shared aging-chip phenotyping infrastructure for JM105 and Intronsaurus:

- `SOURCE — RLS Tracker Round 11 Principal-Supplied Technical Record — 2026-08-07`
- `2026-08-07 — RLS Automation Gate Assessment & HEARTH Socratic Review`
- `MEMO 2026-012 — RLS Automation Integration Across JM105 & Intronsaurus`

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 11 | `rls-tracker/annotation_dashboard.py` | OpenCV interactive dashboard for trap-by-trap navigation of brightfield aging-chip frames; side-by-side human/AI state rendering; keyboard shortcuts; contrast/zoom; writes to `master_human_annotations.xlsx`; smart resume keyed by `Chip_ID`, `Position`, `Trap_ID`, `Frame` | Human annotation UI for the six-class ontology (Mother, Early Bud, Late Bud, Dead Cell, No Cell, Blurry, plus excluded/administrative classes) over >14,000 verified frames | `exact full source not yet recovered`; only prose description found, no `.py`/`.ipynb` file body |
| 12 | `rls-tracker/train_rls_classifier.py` | Round 11 model: ImageNet-pretrained frozen MobileNetV2 backbone, `GlobalAveragePooling2D` -> `Dropout(0.4)` -> `Dense(num_classes)`; Adam lr 1e-3; `ReduceLROnPlateau`(factor 0.5, patience 3); `EarlyStopping`(patience 8); image pipeline: 0.5-99.5 percentile contrast stretch, resize 128x128x3, MobileNetV2 preprocessing to [-1,1], `RandomFlip("vertical")`; per-frame sample weight `ClassWeight x [1 + 0.5x|Human RLS-AI RLS| + 0.5 for missed mortality]` | Frame classifier plus hard-trap mining used to reduce manual post-acquisition aging-chip scoring | `exact full source not yet recovered` |
| 13 | `rls-tracker/rls_sequence_engine.py` | Sequence-aware RLS/censoring/mortality logic: division on Late Bud -> Mother/Early Bud (with No Cell gap look-back); `is_censored`/`died_on_chip` rules keyed on Blurry/Escaped/Skipped and direct-to-Dead-Cell transitions | Converts per-frame classifications into per-trap RLS, death/censoring outcomes for lifespan phenotyping (including the CR x Mud1 arm) | `exact full source not yet recovered` |

No `.py`, `.ipynb`, or other runnable source body for the RLS Tracker was found in Drive or as a Gmail attachment in this pass — only the three descriptive Google Docs above. Nothing was imported or reconstructed from the prose description. This project does not yet have a dedicated top-level folder in the repo; `rls-tracker/` paths here are proposed, pending Jordan confirming placement (this project or a new one) once real source is recovered.

## Recovery pass: 2026-07-12

### Sources searched

File Library semantic/keyword search using five focused queries:

1. `Image001.nd2` + `Image001_Pos0_Hyperstack.tif` + Bio-Formats + Fiji macro.
2. `MitosoxRedInducibleFusionsRepeat.nd2` + `Continue001.nd2` + `Continue002.nd2` + Groovy/ImageJ.
3. `rollingBallRadius=100` + the RLS and ROS output filenames.
4. `JM128` + `JM129` + MitoSOX + aging-chip + Fiji/Groovy.
5. `C=2`, `Z=60`, `T=107/139/145` + virtual hyperstack + background subtraction.

### Search result classification

- No complete Fiji macro body was returned.
- No complete Groovy script body was returned.
- Returned items were primarily JM105 scientific documents/posters, a network dashboard, the D-BIOL program, and already-known language-learning HTML.
- None of the returned items contained an exact runnable microscopy source file.

### Import decision

No runnable microscopy code imported. No code reconstructed from remembered dimensions, paths, frame ranges, or output names.

## Quantitative integrity constraints

- Never silently convert MitoSOX data to 8-bit.
- Never silently apply auto-contrast to quantitative output.
- Treat contrast used only for viewing as display-only and document it explicitly.
- Keep rolling-ball background subtraction explicit, including radius and channel/timepoint scope.
- Preserve raw bit depth and distinguish raw, background-subtracted, display-adjusted, and merged outputs.
- Do not commit ND2, TIFF stacks, generated microscopy outputs, caches, or temporary exports.

## Code-focused risk and containment

**Risk:** enough detailed workflow metadata exists to tempt reconstruction of plausible-looking macros that may differ from the exact historical code in channel ordering, Bio-Formats calls, frame indexing, bit depth, or saving behavior.

**Containment:** this ledger is the single source of truth for unrecovered microscopy scripts. A candidate becomes canonical only after complete source is found and checked against the documented dimensions, paths, outputs, and quantitative guardrails.
