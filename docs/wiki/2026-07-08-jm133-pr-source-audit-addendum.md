# Wiki addendum — 2026-07-08 — JM133 PR source audit

## Summary

The JM-133 weak-5SS/Mud1 analysis is no longer merely a filename/source clue. Exact runnable source exists in GitHub PR #1 on branch `legacy-code-backfill-2026-07-08`, but it is not yet on `main`.

## Exact recovered source location

```text
PR #1: Legacy code backfill: JM133 and recovery docs
branch: legacy-code-backfill-2026-07-08
state at audit: open
mergeable at audit: false
```

Files in the PR:

```text
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch
```

## Main-branch project folder created

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/README.md
```

This folder records the intended canonical project location and source constraints without duplicating partial code.

## Intended canonical target paths after reconciliation

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.py
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.sbatch
```

## Scientific/data status

- Real JM105 total/rRNA-depleted RNA-seq / intron-feature analysis only.
- No fake biological data.
- Uses Mud1-dependence and 5′SS:U1-pairing logic for the JM-133 question: “Do weak 5′ splice sites need Mud1?”
- The script distinguishes raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on logic and does not treat CR as starvation.

## Current non-recovered source targets checked in this continuation

Google Drive and project-context searches did not recover complete source for:

```text
JM128/JM129 Fiji .ijm and Groovy microscopy macros
kartoffel_vocabulary_active_recall_WORKING.html
german-drill-6.html
runnable Figure 5 PowerShell/Bash/Python renderer source
```

The Drive lab notebook did recover historical JM-076 macro path clues, including:

```text
Y:\Jordan\JM076\Macros\Step1_DetectAdjustConvertResize.ijm
Y:\Jordan\JM076\Macros\Step2_BriightfieldExtractor.ijm
Y:\Jordan\JM076\Macros\Step_3ConvertResize.ijm
Y:\Jordan\JM076\Macros\Step4_RemovebrightfieldSlicesFromStack.ijm
Y:\Jordan\JM076\Macros\Step6_RedChannelMacro.ijm
```

These remain recovery targets, not imported code.
