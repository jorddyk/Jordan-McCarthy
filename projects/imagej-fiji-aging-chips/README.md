# ImageJ / Fiji Aging-Chip Macros

Human goal: preserve the Fiji/ImageJ macros and Groovy scripts that help process and analyze yeast aging-chip and MAD/aging microscopy datasets.

This project is for runnable Fiji `.ijm` macros, Groovy scripts, and small helper documentation. It is not for raw `.nd2`, TIFF stacks, or generated image outputs.

## Intended structure

```text
projects/imagej-fiji-aging-chips/
  macros/
    Fiji `.ijm` macros.
  groovy/
    Fiji/Groovy scripts for jobs too complex for the macro language.
  docs/
    Notes on inputs, outputs, channel/timepoint conventions, and known failure modes.
  README.md
```

## Priority legacy code to recover

These are the highest-priority historical scripts to recover from old ChatGPT chats or uploaded files. Do not recreate them as if they were recovered; import exact full source when available.

| Priority | Proposed canonical path | Known historical source / purpose | Current status |
|---|---|---|---|
| 1 | `macros/jm128-split-nd2-positions-bioformats.ijm` | JM128 split `Image001.nd2` into separate position hyperstacks using Bio-Formats Macro Extensions; input `Y:\Laura\JM128 How do superoxide levels change during aging\Nup60Gcn5MitosoxRed_raw_data\Image001.nd2`; output folder `Y:\Laura\JM128 How do superoxide levels change during aging\seperate_positions`; output names like `Image001_Pos0_Hyperstack.tif` | Exact full macro not yet recovered |
| 2 | `macros/jm128-extract-mitosox-c2-every6-zpositions.ijm` | JM128-style ND2 split/extract: `C=2, Z=60, T=107`; C1 brightfield, C2 MitoSOX; real frames `T=1,7,13,19...`; output hyperstack `C=1, Z=60, T=18`; title `MitoSOX_only_C2_T1_every6_Zpositions` | Exact full macro not yet recovered |
| 3 | `macros/jm128-stitch-image-and-image001-brightfield-rls.ijm` | Stitch `Image.nd2` + `Image001.nd2`; keep BF only; 30 positions; downscale to `1024x1022`; concatenate file1 then file2; output `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif` ... `Pos29.tif`; save to `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions/RLS/` | Exact full macro not yet recovered |
| 4 | `macros/jm128-merge-ros-bf-fl.ijm` | Merge `PosX_BF.tif` + `PosX_FL.tif` from `.../seperate_positions/ROS/`; output to `.../ROS/Merge/`; output `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif`; `outputOffset = 1`, `firstSourcePos = 0`, `lastSourcePos = 29`; applies frame-1 auto-style contrast for visualization; saves merged TIFFs without altering originals | Exact full macro not yet recovered |
| 5 | `groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy` | JM129 MitoSOX script for `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`; dimensions `2048x2044`, `C=2`, `Z=60`, `T=107/139/145`; global ranges `1-107`, `108-246`, `247-391`; output virtual hyperstack `C=1, Z=60, T=66` or equivalent real MitoSOX frames; rolling-ball background subtraction `100 px`; no 8-bit conversion/auto-contrast for quantitative MitoSOX | Exact full Groovy source not yet recovered |

## Additional recovered source clues, not yet source code

The Google Drive document `Lab Notebook complete copy and paste text dump` contains a JM-076 aging-chip processing protocol for intronless nuclear-encoded mitochondrial genes tagged with Tom70-yemScarlet3. It names exact historical Fiji macro paths, but does not contain the macro bodies. These should be recovered from the Windows path or old chat/file artifacts before committing.

| Historical macro path | Proposed canonical path | Purpose inferred from protocol | Current status |
|---|---|---|---|
| `Y:\Jordan\JM076\Macros\Step1_DetectAdjustConvertResize.ijm` | `macros/jm076-detect-adjust-convert-resize.ijm` | First-pass processing of OME-TIFF aging-chip position chunks before manual/stack concatenation. | Exact full source not yet recovered; do not reconstruct from protocol summary |
| `Y:\Jordan\JM076\Macros\Step2_BriightfieldExtractor.ijm` | `macros/jm076-brightfield-extractor.ijm` | Extract brightfield stack after chunk concatenation; historical filename spelling `Briightfield` preserved as a source clue. | Exact full source not yet recovered; do not reconstruct from protocol summary |
| `Y:\Jordan\JM076\Macros\Step_3ConvertResize.ijm` | `macros/jm076-convert-resize.ijm` | Convert/resize channel stack before brightfield-slice removal and red-channel extraction. | Exact full source not yet recovered; do not reconstruct from protocol summary |
| `Y:\Jordan\JM076\Macros\Step4_RemovebrightfieldSlicesFromStack.ijm` | `macros/jm076-remove-brightfield-slices-from-stack.ijm` | Remove brightfield slices from a combined aging-chip stack. | Exact full source not yet recovered; do not reconstruct from protocol summary |
| `Y:\Jordan\JM076\Macros\Step6_RedChannelMacro.ijm` | `macros/jm076-red-channel-extractor.ijm` | Extract red-channel mitochondrial signal before saving, inversion, and MultiStackReg registration. | Exact full source not yet recovered; do not reconstruct from protocol summary |

## Quantification guardrails

- For MitoSOX quantitative analysis, do not convert to 8-bit.
- Do not apply auto-contrast to quantitative data.
- Background subtraction should be explicit and documented, for example rolling-ball `100 px` when that was the validated workflow.
- Keep raw ND2 files out of GitHub.
- Preserve channel/timepoint conventions in README comments near each macro.

## Latest recovery pass — 2026-07-12

File Library was searched using the exact source clues `Image001.nd2`, `Image001_Pos0_Hyperstack.tif`, `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`, `rollingBallRadius=100`, `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif`, `Nup60Gcn5MitoSoxRed_ROS_Pos`, `C=2`, `Z=60`, and `T=107/139/145`.

No result contained a complete `.ijm` or Groovy source body. Results were unrelated scientific documents, posters, and already-canonical language-learning HTML. Therefore no microscopy code was imported or reconstructed. Detailed recovery evidence is tracked in `docs/legacy-code-backfill.md`.

## Import rule

A macro/script becomes canonical only when the complete exact source is available. If only a summary of the historical script is available, keep it in this README or the legacy backfill record as a recovery target rather than committing reconstructed code as recovered code.

## Candidate scope addition: RLS Tracker & AI Engine

A Python/Keras "Yeast Cell Replicative Lifespan (RLS) Tracker & AI Engine" (OpenCV annotation UI, MobileNetV2 frame-state classifier, sequence-based RLS/mortality/censoring engine, and a prospective-lifespan oracle) was identified as principal-supplied source in Google Drive on 2026-08-07/08-09. It converts longitudinal aging-chip brightfield stacks into per-trap RLS outputs and is a natural fit for this project's scope even though it is Python rather than Fiji/ImageJ. It is proposed to live under `python/rls-tracker/` once exact source is recovered. See `docs/legacy-code-backfill.md` for the full recovery-clue record; no source has been recovered yet.
