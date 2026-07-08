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
| 1 | `macros/jm128-split-nd2-positions-bioformats.ijm` | JM128 split `Image001.nd2` into separate position hyperstacks using Bio-Formats Macro Extensions; input `Y:\Laura\JM128 How do superoxide levels change during aging\Nup60Gcn5MitosoxRed_raw_data\Image001.nd2`; output folder `Y:\Laura\JM128 How do superoxide levels change during aging\seperate_positions`; output names like `Image001_Pos0_Hyperstack.tif` | Exact full macro not yet recovered in this run |
| 2 | `macros/jm128-extract-mitosox-c2-every6-zpositions.ijm` | JM128-style ND2 split/extract: `C=2, Z=60, T=107`; C1 brightfield, C2 MitoSOX; real frames `T=1,7,13,19...`; output hyperstack `C=1, Z=60, T=18`; title `MitoSOX_only_C2_T1_every6_Zpositions` | Exact full macro not yet recovered in this run |
| 3 | `macros/jm128-stitch-image-and-image001-brightfield-rls.ijm` | Stitch `Image.nd2` + `Image001.nd2`; keep BF only; 30 positions; downscale to `1024x1022`; concatenate file1 then file2; output `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif` ... `Pos29.tif`; save to `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions/RLS/` | Exact full macro not yet recovered in this run |
| 4 | `macros/jm128-merge-ros-bf-fl.ijm` | Merge `PosX_BF.tif` + `PosX_FL.tif` from `.../seperate_positions/ROS/`; output to `.../ROS/Merge/`; output `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif`; `outputOffset = 1`, `firstSourcePos = 0`, `lastSourcePos = 29`; applies frame-1 auto-style contrast for visualization; saves merged TIFFs without altering originals | Exact full macro not yet recovered in this run |
| 5 | `groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy` | JM129 MitoSOX script for `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`; dimensions `2048x2044`, `C=2`, `Z=60`, `T=107/139/145`; global ranges `1-107`, `108-246`, `247-391`; output virtual hyperstack `C=1, Z=60, T=66` or equivalent real MitoSOX frames; rolling-ball background subtraction `100 px`; no 8-bit conversion/auto-contrast for quantitative MitoSOX | Exact full Groovy source not yet recovered in this run |

## Quantification guardrails

- For MitoSOX quantitative analysis, do not convert to 8-bit.
- Do not apply auto-contrast to quantitative data.
- Background subtraction should be explicit and documented, for example rolling-ball `100 px` when that was the validated workflow.
- Keep raw ND2 files out of GitHub.
- Preserve channel/timepoint conventions in README comments near each macro.

## Import rule

A macro/script becomes canonical only when the complete exact source is available. If only a summary of the historical script is available, keep it in this README as a recovery target rather than committing reconstructed code as recovered code.
