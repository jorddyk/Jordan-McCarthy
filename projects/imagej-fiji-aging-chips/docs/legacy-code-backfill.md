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

## New priority target: RLS Tracker & AI Engine (identified 2026-08-09)

A Google Drive document ("SOURCE — RLS Tracker Round 11 Principal-Supplied Technical Record — 2026-08-07", Tier-1 owner-supplied evidence, updated with a "FINAL CODE-ARCHITECTURE UPDATE — 7 AUGUST 2026" section) describes a Python/Keras aging-chip analysis system that is a candidate addition to this project area. It is not yet represented anywhere in this repository.

| Priority | Proposed human filename | Source clue | Status |
|---|---|---|---|
| 11 | `python/rls-tracker/train_classifier.py` | Named directly in the 2026-08-07 Drive record as reviewed in an active conversation; MobileNetV2 (ImageNet-pretrained, frozen backbone) → GlobalAveragePooling2D → Dropout(0.4) → Dense(num_classes) frame-state classifier over 128×128×3 RGB brightfield-trap frames (0.5th–99.5th percentile contrast stretch, MobileNetV2 preprocessing to [-1,1]); Adam lr=1e-3, ReduceLROnPlateau(factor=0.5, patience=3), EarlyStopping(patience=8); per-frame sample weight `ClassWeight × [1.0 + 0.5×|Human RLS − AI RLS| + (0.5 if missed mortality else 0)]`; frame-level stratified 80/20 split | `exact full source not yet recovered` |
| 12 | `python/rls-tracker/human_classifier_ui.py` | Named directly in the same 2026-08-07 Drive record; OpenCV interactive single-cell trap-frame annotation dashboard with human-vs-AI side-by-side rendering, keyboard shortcuts, contrast/zoom controls, and persistence to `master_human_annotations.xlsx`; state ontology Mother/Early Bud/Late Bud/Dead Cell/No Cell/Escaped/Blurry/Skipped; smart resume keyed by `Chip_ID`, `Position`, `Trap_ID`, `Frame` | `exact full source not yet recovered` |
| 13 | `python/rls-tracker/rls-sequence-engine` (component, filename not yet supplied) | Same source: deterministic sequence layer converting ordered frame labels into division events (Late Bud → Mother/Early Bud in consecutive frames, or across a No Cell gap, = +1 RLS), mortality (living state → Dead Cell), and censoring (Blurry/Escaped/Skipped anywhere up to death) | `exact full source not yet recovered`; component name/file not yet identified in source record |
| 14 | `python/rls-tracker/lifespan-oracle` (component, filename not yet supplied) | Same source: prospective-lifespan MLP trained on 22 trajectory-summary features (current RLS, frames observed, state fractions, interdivision-interval stats/trend/variability, classifier-confidence summaries) after ≥3 observed divisions; predicts q10/q50/q90 remaining-division quantiles via pinball loss; whole-trap identity held out between train/validation | `exact full source not yet recovered`; component name/file not yet identified in source record |

This is a description of code architecture reviewed in a chat, not the source code itself — per the recovery standard above, filenames, architecture summaries, and hyperparameters are recovery clues only. Do not reconstruct `train_classifier.py`, `human_classifier_ui.py`, or the sequence/oracle components from this description. The next recovery pass should request the exact `.py` file bodies (or a Drive/File Library upload of them) directly.

Also note (Tier-3, not a source fact): the same Drive record flags its own open validation questions — frame-level (not trap-level) train/validation splitting for the primary classifier, hard-trap sample weights generated before primary training, `Chip_ID` omitted from the TIFF lookup identity in `train_classifier.py`, and a confidence-feature train/inference mismatch. These should be checked once the exact source is recovered, not assumed resolved.
