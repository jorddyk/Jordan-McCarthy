# JM105 Nature Aging Figure Bible — Locked Canonical Specification

**Canonical version:** `JM105-FIGURE-BIBLE-v1.0-2026-07-22`  
**Status:** LOCKED working bible for all JM105/Nature Aging figure analysis, panel design, rendering, and review.

## Mandatory reference rule

Every future JM105 figure answer, panel decision, rendering script, render audit, or figure revision must explicitly state:

> **Bible reference: JM105-FIGURE-BIBLE-v1.0-2026-07-22, Figure X / Panel X.**

A response that does not reference this bible is incomplete. The reference must identify the relevant figure/panel whenever a panel exists. General questions cite the bible version and the governing section.

## Non-negotiable project contract

1. No information is removed to relieve crowding. Every specified object appears.
2. Emit a lane map before writing rendering code. Every object maps to exactly one lane and anchor.
3. Emit a collision inventory before patching. Name exact object pairs and resolutions.
4. Code is complete and runnable on EULER and PowerShell as delivered.
5. Canvas dimensions are fixed and declared. Never infer the canvas from content.
6. `bbox_inches="tight"` is forbidden.
7. Every render emits transparent SVG, transparent PDF, transparent PNG, and white-background preview PNG.
8. SVG text stays editable (`svg.fonttype = "none"`) and Arial-requested; text must never be outlined.
9. Figure 2 uses only total/rRNA-depleted JM105. Poly-A, P-versus-T, mRNA-like and P−T constructs are outside the allowlist.
10. Definitions used in code must be repeated as comments where used:
    - `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`
    - `candidate_score = min(aging_effect, CR_suppression)`
    - Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression), with data-driven y-limits.
11. Panel F x-ticks, genotype labels, right-stats and footnote occupy separate lanes.
12. Final self-audit reports what was checked in each lane and each collision category.

## Locked semantic colour system

One semantic diverging axis runs through the paper:

- warm vermillion = increased / aged / worse;
- grey = unchanged / reference;
- cool blue = restricted / suppressed / protected.

Reference levels are always grey: young, 2% glucose, WT MUD1, UPF1+, intron present and background introns. Each variable owns one hue and never changes it. When hue is unavailable, use marker shape, open/filled state or facets. Candidate introns receive no independent hue; they retain condition colour and are promoted with a black outline.

Every panel script begins:

```python
from paper_style import *
set_paper_style()
```

Colours are never defined locally.

## Canonical Google Drive source

- [Locked Google Drive folder](https://drive.google.com/drive/folders/1qrmTGvzWtI_SZ2CBAzk-HL8lFl8b2zLB)
- [Native Google Doc](https://docs.google.com/document/d/1aytYln182XsiYBNX4iH_UWK97wuai-Y_Tn77G6pbeVc/edit)
- [Locked DOCX copy](https://docs.google.com/document/d/1qhl3irfYUZ4B4r_ktFby2Xg0JiGtnx0E/edit)

## Canonical files

- `JM105_Figure_Bible_LOCKED_2026-07-22.docx` — complete human-readable bible.
- `JM105_Figure_Bible_LOCKED_2026-07-22.md` — searchable canonical text.
- `JM105_panel_manifest.json` — machine-readable panel contract.
- `paper_style.py` — mandatory imported visual system and fixed-output helper.
- `SHA256SUMS.txt` — integrity manifest.

## Scope of this version

This version contains all six figure architectures and all 45 panel specifications, including the concrete question, content, visual grammar and one-panel beauty/consistency tweak. Figure 6 remains conditional and must pass the admission criteria in the bible before it enters the main paper.
