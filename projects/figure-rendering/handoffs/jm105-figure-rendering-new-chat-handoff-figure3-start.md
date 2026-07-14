# JM105 / Intronsaurus figure rendering handoff — move to Figure 3

This handoff captures the current anti-drift state for the JM105 / Intronsaurus / Nature Aging figure-rendering project.

## Project goal

Turn the five-figure JM105 / Intronsaurus manuscript draft into a coherent, beautiful, reviewer-defensible Nature Aging-style paper, without proposing new experiments.

Central manuscript claim:

> Aging exposes an NMD-hidden retained-intron RNA state in yeast; caloric restriction suppresses part of this state through Mud1-dependent protection of architecturally vulnerable introns.

## Anti-drift source of truth

Google Sheet:

- `JM105 Intronsaurus Figure Acceptance Matrix`
- URL: https://docs.google.com/spreadsheets/d/16871n65yJu4wc-kmoqjEYPgE8sPdP7xBn2aTkukcUSg/edit?usp=drivesdk

Tabs:

- `Acceptance Matrix`
- `Definitions Lock`
- `Action Log`
- `Decision Rules`
- `Figure Order`
- `Self Score`

Update this matrix after every meaningful action: GitHub search, source discovery, render attempt, render failure, inspection, patch, conceptual decision, accepted panel, rejected panel, or GitHub commit.

## GitHub canonical repo

Repository:

- `jorddyk/Jordan-McCarthy`

Important existing paths:

- `projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md`
- `projects/figure-rendering/templates/jm132-cell-cycle-rendering-rules.md`
- `projects/figure-rendering/panel-renderers/jm105-rendering-harness/README.md`
- `projects/figure-rendering/panel-renderers/jm105-rendering-harness/jm105_source_inventory.py`
- `projects/figure-rendering/panel-renderers/jm105-rendering-harness/run-jm105-source-inventory-from-windows.ps1`
- `projects/figure-rendering/README.md`

Before writing new code, search GitHub carefully for prior renderers, standards, and source-discovery logic. Do not assume the repo lacks useful code.

## Figure order

The intended order was:

1. Figure 2 — lock central CR reversibility claim and target vocabulary.
2. Figure 3 — Mud1 dependence of CR suppression.
3. Figure 4 — architecture of Mud1/CR-sensitive introns.
4. Figure 1 — onboarding/definitions, updated after terms are locked.
5. Figure 5 — synthesis / Mud1-GFP / starvation context / model.

Current instruction from Jordan: we can move on to the next figure. Start new work from **Figure 3** unless Jordan explicitly asks to rescue Figure 2 first.

## Figure 2 current status

Figure 2 was started as the first canonical anti-drift renderer but is not locked.

A PowerShell/Euler render attempt failed before rendering panels because of a typo in the Python renderer:

```text
NameError: name 'threshold_c' is not defined. Did you mean: 'threshold_cr'?
```

Important details:

- Python environment worked: matplotlib, pandas, numpy, PIL imported successfully.
- Source discovery worked.
- Source discovery selected the strict Figure 2 table:
  `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_metrics_all.tsv`
- Expected rows from the failed discovery: 402.
- Failed remote run directory:
  `/cluster/home/jmccarthy/JM105_Figure2_public_final_20260713_171245`
- Failed local output directory:
  `C:\Users\jmccarthy\Downloads\JM105_Figure2_public_final_20260713_171245\out`

A surgical rescue plan exists: replace `threshold_c` with `threshold_cr` in the existing remote script and rerun. Do not rewrite the entire Figure 2 renderer unless Jordan asks or the rescue reveals deeper problems.

If returning to Figure 2 later, inspect:

- contact sheet
- individual panels B, D, E, F
- `Figure2_public_final_run_summary.json`
- `audits/Figure2_source_discovery.tsv`
- `audits/Figure2_common_name_resolution_audit.tsv`
- `audits/Figure2_IR_column_resolution.tsv`
- `audits/Figure2_lane_map.tsv`
- `audits/Figure2_collision_inventory.tsv`
- `audits/Figure2_final_self_audit.tsv`

## Locked definitions

Use these exact definitions in code comments where used:

- `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`
- `aging_effect = NMD_hidden(old 2%) − NMD_hidden(young 2%)`
- `CR_suppression(+MUD1) = NMD_hidden(old 2%) − NMD_hidden(old CR)`
- `candidate_score = min(aging_effect, CR_suppression)`
- Later Figure 4/F definition: `Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression); y-limits data-driven from computed values, not hardcoded.`

## Rendering invariants

- No information is removed merely to relieve crowding.
- Do not use `bbox_inches="tight"`.
- Fixed canvas dimensions only.
- Code must be complete and runnable as delivered.
- No placeholders, ellipses, or “same as above.”
- SVG text must remain editable text; use `svg.fonttype = "none"`.
- Before code, emit a lane map assigning every object to a lane.
- Before patching, emit a collision inventory naming exact object pairs and resolutions.
- Output fixed-dimension transparent SVG + PDF + PNG plus a white-background preview PNG.
- Visible gene labels should use common/public gene names, not systematic ORF/intron IDs, unless truly unavoidable and explicitly audited.
- Do not show “JM105” in public-facing panel labels.
- If a source is missing or provenance-insecure, fail or render a source-gated placeholder; do not fake data.

## Scope fences

Figure 2 RNA panels:

- total/rRNA-depleted JM105 only.
- no poly-A.
- no P-versus-T.
- no mRNA-like logic.
- no P−T construct logic.

For later figures, maintain the same target vocabulary:

- aging-linked introns
- CR-suppressed aging introns
- Mud1/CR-sensitive introns
- starvation-matched subset, when using Parenteau context

## Current next task: Figure 3

Start with Figure 3 acceptance lock, not rendering immediately.

Figure 3 role:

> Test whether Mud1 is required for the CR suppression of age-linked retained-intron leakage.

Figure 3 should inherit Figure 2 vocabulary. Do not invent new names for the same target sets.

Likely Figure 3 components from current deck:

- A: lifespan / genotype context, if source-secure.
- B: set-level Mud1 dependence of CR suppression.
- C: candidate-by-candidate +MUD1 versus mud1Δ CR suppression.
- D/E/F: candidate-level behavior/ranking/profiles, likely overpacked and may need simplification.
- G: host RNA abundance control.
- H: cell-cycle slowing control.

Known Figure 3 issue:

The science is strong, but the figure is visually overpacked. It must distinguish proof panels from controls. Do not make every control compete visually with the main causal result.

Recommended Figure 3 first action:

1. Update Google Sheet Action Log: starting Figure 3 acceptance lock; Figure 2 renderer failed due to typo and is pending rescue later.
2. Search GitHub for Figure 3 / JM105 / Mud1 / `CR_suppression` / `mud1` renderers or source inventories.
3. Create a Figure 3 acceptance matrix row-by-row:
   - panel
   - exact claim
   - evidence shown
   - objection answered
   - main/support/control/audit/supplement status
   - source path needed
   - visible labels required
   - drift risk
4. Only after the panel claims are locked, write complete rendering code.

## Avoid repeated mistakes

- Do not render empty/fake panels when source matching fails.
- Do not let legends, titles, labels, or right-stat text spill off the canvas.
- Do not use systematic ORF IDs as public labels when common names exist.
- Do not produce tiny dashboard panels.
- Do not make the plot island small inside a huge canvas.
- Do not call the public-facing axes “JM105.”
- Do not include candidate score as a visible biological contrast unless explained and necessary.
- Do not use a weak statistical footnote as a main panel.
- Do not rewrite a whole renderer when a surgical patch is enough.
- Do not proceed after a failed `scp`, failed `mkdir`, or failed Python run; check `$LASTEXITCODE` and stop.

## No new experiments

Do not propose new experiments. Work only on figure logic, source locking, rendering, GitHub commits, and anti-drift documentation.
