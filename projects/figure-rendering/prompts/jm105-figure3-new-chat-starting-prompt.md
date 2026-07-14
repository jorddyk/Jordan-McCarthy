# Starting prompt for the next chat: JM105 Figure 3

You are taking over Jordan McCarthy’s Nature Aging / JM105 figure-rendering pipeline at **Figure 3**.

Jordan will upload:

1. the PowerPoint containing all current manuscript figures;
2. the current Yves flow/story document.

Do not start by inventing a layout or renderer. First inspect those uploaded files, the Google Drive acceptance spreadsheet, and the canonical GitHub rendering code described below.

## Mandatory sources to read before code

GitHub repository: `jorddyk/Jordan-McCarthy`

Read in this order:

```text
projects/figure-rendering/START_HERE_FOR_FIGURE_RENDERING.md
projects/figure-rendering/AGENTS.md
projects/figure-rendering/docs/figure-rendering-reliability-standard.md
projects/figure-rendering/templates/figure-rendering-new-chat-checklist.md
projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md
projects/figure-rendering/docs/jm105-figure2-2026-07-14-complete-incident-postmortem.md
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/README.md
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/materialize_exact_renderer.py
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/run_JM105_Figure2_v4_1_on_euler.sh
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/run_JM105_Figure2_v4_1_from_PowerShell.ps1
projects/figure-rendering/qa/hard_collision_gate.py
projects/figure-rendering/panel-renderers/jm132-cell-cycle-fig3h/README.md
projects/figure-rendering/panel-renderers/jm132-cell-cycle-fig3h/run_jm132_fig3h_g_column_10min_y400.ps1
```

Also inspect the Google Drive spreadsheet:

```text
JM105 Intronsaurus Figure Acceptance Matrix
```

Read at minimum:

- `Acceptance Matrix`, Figure 3 rows A–H;
- `Definitions Lock`;
- `Decision Rules`;
- `Figure Order`;
- `Action Log`.

Figure 3 is the next pipeline figure because Figure 2 defines the locked target set and Figure 3 tests whether CR suppression requires Mud1.

## The Figure 2 v4.1 renderer is a proven engineering scaffold

The exact renderer that actually succeeded is now stored in GitHub as six exact source parts plus a SHA256-verifying materializer:

```text
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/
```

Run:

```bash
python3 materialize_exact_renderer.py
```

The reconstructed Python renderer is accepted only if its SHA256 is:

```text
167ac8ffd306ce5e6fb234a4ed3c35eea5b8f2be7205b0df46c1b4f5b28ec593
```

Use the Figure 2 code as a starting point for **engineering**, including:

- fixed millimetre canvas constants;
- panel-specific render functions plus a separate composite function;
- transparent SVG/PDF/PNG and white previews;
- editable SVG text settings;
- explicit font resolution;
- Liberation Sans and DejaVu Sans cross-font testing;
- post-draw clipping and pairwise text-overlap checks;
- point-versus-direct-label collision checks;
- legend-versus-data collision checks;
- visible systematic-ORF rejection;
- lane-map and collision-inventory exports;
- fail-closed source/schema/output validation;
- PowerShell → Euler upload/render → direct `scp -r` retrieval;
- local output verification and white-preview opening before reporting success.

Do **not** reuse Figure 2’s biology, source paths, labels, panel dimensions, candidate logic, axes, colors, or panel layout. Derive all of those from Figure 3’s current PowerPoint, Yves flow, Drive matrix, and verified sources.

For the cell-cycle control, Figure 3H may use the successful JM132 cell-cycle renderer as an engineering and source-parsing scaffold, but first verify that Figure 3H uses the same workbook semantics. Do not assume the JM132 biological parsing rules apply to a different source without inspection.

## Current Figure 3 identity baseline

The uploaded current PowerPoint defines these eight starting panel identities:

```text
A  mud1Δ weakens the CR lifespan benefit
B  CR suppression is reduced without Mud1
C  Most selected introns suppress better with Mud1
D  Candidate-by-candidate CR responses reveal Mud1 dependence
E  Ranking introns by Mud1-dependent CR suppression
F  Representative introns lose CR suppression in mud1Δ
G  Host RNA abundance does not explain the intron effect
H  mud1Δ does not cause gross cell-cycle slowing
```

These are identity/source baselines, not proof that the current equal-size layout or typography is acceptable.

## Important PowerPoint-versus-Drive mismatch

The current PowerPoint letters and the Drive acceptance-matrix descriptions are not perfectly aligned for panels C–F. Before rendering, make a crosswalk table with exactly these columns:

```text
current PowerPoint letter
authoritative current title
current visual/analysis type
Drive matrix row/claim
Yves-flow role
proposed new letter/role
keep / merge as inset / demote / supplement
source table or workbook
```

Do not assume that “Panel C” in the spreadsheet is the same current asset as PowerPoint Panel C. Match by biological analysis and source, not letter alone.

Do not silently delete information. If panels are merged or demoted, preserve the underlying analysis in an inset, exported table, audit, or explicitly proposed supplement and obtain Jordan’s approval before finalizing the new panel map.

## Figure 3 scientific lock

Main causal claim:

> Without Mud1, caloric restriction no longer provides the same suppression of the locked age-linked intron-retention state; candidate examples and controls show that this is not explained by host-RNA abundance or gross sickness/cell-cycle slowing.

Data scope:

- JM105 total / rRNA-depleted data only for RNA-seq panels;
- no poly-A, P-versus-T, mRNA-like, or P−T constructs;
- use the source-clean locked Figure 2/3 candidate set;
- common gene names only on visible panels;
- systematic IDs remain in provenance/audits.

Definitions:

```text
NMD_hidden = IR(upf1Δ) − IR(UPF1+)

CR_suppression(genotype)
= NMD_hidden(old 2%, genotype)
− NMD_hidden(old 0.1% CR, genotype)

Mud1-dependent CR suppression
= CR_suppression(+MUD1)
− CR_suppression(mud1Δ)
```

The public Figure 3 metric is Mud1-dependent CR suppression. Do not display `candidate_score` as a Figure 3 concept.

Safe control wording:

- G: host RNA abundance does not explain the retained-intron CR/Mud1 signal; do not claim host RNA never changes.
- H: the measured cell-cycle/growth control does not support gross slowing as the trivial explanation; do not overstate beyond the actual assay.

## Visual hierarchy to test, not blindly obey

The following is an informed design hypothesis from a prior AI critique. Evaluate it against the PowerPoint, Yves flow, source tables, and Drive matrix. Keep the useful visual diagnosis, but do not treat its panel lettering or exact layout as authoritative.

1. Make the direct Mud1-dependence comparison the visual hero.
   - Preferred candidate-level view:

   ```text
   x = CR_suppression(mud1Δ)
   y = CR_suppression(+MUD1)
   ```

   - include the `y=x` diagonal;
   - use the source-clean locked candidate set;
   - give the hero the largest plot footprint;
   - reader should understand the genetic result in about five seconds.

2. Fold the redundant “most introns suppress better with Mud1” analysis into a compact right-stat/inset attached to the hero when it uses the same points.

   Candidate statistics to verify and show only if source-supported:

   ```text
   number / fraction above diagonal
   median Mud1-dependent CR suppression
   paired or intron-level p value
   exact n
   ```

3. Candidate-detail views should not all remain equal full panels.
   - Prefer one biologically intuitive paired candidate-response panel in the main figure.
   - A full ranking can become a narrow side strip or supplement if it duplicates the same conclusion.
   - Export the complete ranking table regardless.

4. Representative examples should show about 3–4 introns with identical condition order:

   ```text
   +MUD1 old 2%
   +MUD1 old CR
   mud1Δ old 2%
   mud1Δ old CR
   ```

   Use raw IR only when provenance is secure. Otherwise use honestly labeled NMD-hidden profiles and export the raw/source audit. Never fabricate raw traces.

5. G and H are controls and must be visually subordinate to the causal hero.
   - use restrained color;
   - use explicit “control” wording where useful;
   - do not let them compete with the main Mud1-dependence comparison.

6. A is biological context, not the RNA-seq proof.
   - keep the lifespan effect clear and source-secure;
   - use a smaller context slot than the hero;
   - put compact statistics in a dedicated lane.

7. The current slide’s eight near-equal boxes are likely the main visual problem. Explore a hierarchy such as:

   ```text
   top:    small A context | large hero comparison + right-stat inset
   bottom: candidate response/detail | representative examples | small G/H controls
   ```

   This is a starting hypothesis. Produce at least two measured layout options using the actual panel aspect ratios and objects before selecting one.

## First required deliverable in the new chat

After the PowerPoint and Yves flow are uploaded, and before code, provide:

1. a source-grounded Figure 3 panel crosswalk;
2. the one-sentence biological job of each retained analysis;
3. a proposed main/supplement hierarchy;
4. two candidate composite layouts with measured panel slots/aspect ratios;
5. the full lane map for the proposed main-figure layout;
6. the exact collision inventory from the current slide and proposed geometry;
7. a source manifest with exact paths, schemas, row/group counts, and unresolved inputs;
8. a decision on which current analyses merge, remain full panels, become insets, or move to supplement.

If required sources are unresolved, stop with the exact missing-source list. Do not substitute mock data or reuse a visually similar Figure 2 panel.

## Rendering and delivery contract

Once sources and hierarchy are locked:

- render the complete agreed Figure 3 scope, not a convenient subset;
- use fixed canvases and preserve approved panel aspect ratios;
- no automatic tight crop;
- editable SVG text;
- transparent SVG/PDF/PNG plus white preview for every panel;
- run PowerShell parser, `bash -n`, and `python3 -m py_compile` before delivery;
- run the exact renderer on Euler;
- record the actual resolved font;
- run the complete collision gate under the Euler font and at least one fallback;
- zero clipping, text overlap, legend-data overlap, point-label overlap, or visible systematic IDs;
- retrieve all outputs to Windows with direct `scp -r`;
- verify all local files before printing success;
- open the white contact sheet automatically;
- update the Drive Action Log and GitHub after each material failure, correction, render, or acceptance decision;
- commit only the accepted canonical Figure 3 renderer and lessons learned.

Do not say that a render is complete until the full upload → Euler render → remote verification → retrieval → local verification → preview-open route has passed.
