# JM105 Figure 2 authoritative panel change lock

Date: 2026-07-14

This file mirrors the current authoritative Figure 2 rows in the Google Drive spreadsheet `JM105 Intronsaurus Figure Acceptance Matrix`. Future chats must consult this file together with `templates/chatgpt-jm105-rendering-operating-standard.md` before rendering Figure 2.

## Global locks

- RNA scope: total / rRNA-depleted JM105 only.
- Forbidden: poly-A, P-versus-T, mRNA-like, P−T, starvation wording for 0.1% glucose CR.
- `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`.
- `candidate_score = min(aging_effect, CR_suppression)`.
- Visible gene labels: standard/common names only; systematic IDs are provenance/audit fields only.
- No visible internal `JM105` naming in publication-facing labels.
- Fixed canvas, no automatic tight cropping, editable SVG text, transparent SVG/PDF/PNG plus white preview.
- Lane map and exact collision inventory precede code.
- Every response that causes or reports a successful Euler render must also provide the exact PowerShell retrieval command for that exact confirmed remote output directory. A render is not a complete deliverable until the user can download it.
- The retrieval command must use a confirmed remote directory, create a deterministic local Downloads folder, use direct `scp -r`, verify the local folder and at least one preview PNG, then open the contact sheet or local output folder. Do not omit retrieval, defer it to a later response, or make the user infer the path.
- When Jordan asks to rerender a complete figure, the execution scope is every panel in that figure. For Figure 2, that means A, B, C, D, E, and F. A subset render is allowed only when Jordan explicitly requests a subset or explicitly approves a staged subset.
- The current supplied composite/deck fixes panel identity before redesign. Figure 2A is the lifespan panel, Figure 2B is the age-effect versus CR-suppression scatter, Figure 2C is the quadrant-definition panel, Figure 2D is the ranked-candidate panel, Figure 2E is the raw NMD-on/off profile panel, and Figure 2F is the gate hierarchy. Do not replace one biological panel type with another without Jordan's explicit approval.
- An acceptance-matrix row describing a possible replacement is not permission to change panel identity when the current composite shows a specific panel. If the matrix and current composite appear inconsistent, stop and reconcile them before rendering.

## Panel A — CR intervention/context

Panel identity: lifespan/survival panel showing the CR intervention as a lifespan-extending entry point.

Claim: caloric restriction is the aging intervention being tested in the old-cell RNA-seq design.

Current state: the supplied Figure 2 composite contains the lifespan panel. Preserve that identity. Do not replace it with an RNA-seq condition schematic.

Required change:

- recover and audit the actual lifespan source data and renderer;
- never fake or reconstruct survival values from the raster composite;
- retain the lifespan panel type, survival-probability y-axis, replicative-lifespan x-axis, cohort labels, and statistic once source-verified;
- say CR, not starvation;
- specify glucose only where needed.

## Panel B — hero age × CR state-space

Panel identity: aging effect versus old-cell CR-suppression scatter.

Claim: CR suppresses a defined age-linked NMD-hidden retained-intron state in old cells.

Evidence: aging effect versus old-cell CR suppression for strict eligible introns.

Required change:

- use `pass_strict_nuclear_orf_gate` for the eligible universe;
- use explicit candidate/gate columns rather than recomputing a loose threshold-only set;
- exclude mitochondrial transcript contamination;
- visible labels must be common names only;
- export systematic IDs and exact matched aliases only in TSV/provenance;
- retain a dedicated right-side label lane and no label–point overlap.

## Panel C — quadrant definition

Panel identity: four-quadrant explanatory definition aligned to Panel B.

Claim: aging effect and CR suppression define the target-set state space.

Required change:

- retain all four biological quadrants and their directional definitions;
- retain explicit aging-effect and CR-suppression direction labels;
- preserve the focus callout for age-increased and CR-suppressed candidates;
- dedicated top title/descriptor lane;
- dedicated plot lane;
- dedicated bottom focus/footer lane;
- no clipped left/right descriptors;
- no focus box overlapping the bottom descriptor;
- `candidate_score = min(aging_effect, CR_suppression)` belongs in code/audit or caption unless Jordan explicitly asks for it on-panel; it must not replace the four-quadrant explanation.

## Panel D — ranked named candidates

Panel identity: ranked candidate table/bar panel.

Claim: the strongest CR-suppressed aging introns are real named genes, not anonymous points.

Required change:

- rerank only after the corrected nuclear candidate set is locked;
- no mitochondrial transcript rows;
- common gene names only on the visible panel;
- systematic IDs only in audit/provenance;
- dedicated rank, candidate-label, aging-effect, CR-suppression, and joint-score lanes;
- preserve the conservative-score definition in the footer or caption;
- avoid duplicated labels.

## Panel E — raw NMD-on/off profiles

Panel identity: multi-gene raw NMD-on/off condition profiles.

Claim: raw matched NMD-on/off condition profiles support the computed NMD-hidden CR suppression.

Required change:

- source-lock the raw condition table before rendering;
- fail closed if raw IR columns are unavailable;
- do not render blank axes or an empty legend;
- retain representative-gene small multiples rather than replacing the panel type;
- separate subplot title, legend, x-tick, group-label, and footer lanes;
- code comment must state `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`;
- matched conditions: young 2%, old 2%, old 0.1% CR, with NMD-on and NMD-off shown honestly.

## Panel F — informative validated gate transitions

Panel identity: gate hierarchy/funnel ending in the final candidate-set count.

Claim: gate hierarchy distinguishes the eligible universe, aging-linked, CR-suppressed, and locked candidate sets.

Required change:

- retain the gate-hierarchy panel type;
- show only informative validated transitions;
- remove no-op gates that leave n unchanged;
- export the full gate audit separately;
- no contaminated final n;
- use labels: Universe → aging-linked → CR-suppressed → Mud1/CR-sensitive only when each transition is actually supported;
- x-tick, group-label, right-stat, and footer lanes remain separate if a quantitative comparison is shown.

## Execution rules learned from 2026-07-14 failures

- Work directly on Euler when raw data and renderers are already there.
- Inspect each renderer's CLI before running it; do not infer arguments.
- Run one renderer at a time until outputs and source TSV are confirmed.
- Do not add tar/ZIP/extraction layers without a demonstrated need.
- Do not print success after a failed command.
- Do not treat a path variable as proof a file exists.
- Do not use raw-text regex to infer Python semantics; use AST when auditing `savefig()`.
- A renderer exit code 0 is not source acceptance. Verify gate columns, visible labels, resolved font, collisions, and exported provenance.
- Never end a successful render response without the corresponding PowerShell download block. The exact confirmed remote output path must appear in that same response.
- Never substitute a different biological panel because it is easier to render or because its source is already available.
- Never interpret “rerender Figure 2” as “render whichever Figure 2 panels are convenient.” The default scope is all six panels A–F.
