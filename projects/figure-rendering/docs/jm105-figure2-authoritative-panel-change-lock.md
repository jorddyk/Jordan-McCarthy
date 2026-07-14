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

## Panel A — CR intervention/context

Claim: caloric restriction is the aging intervention being tested in the old-cell RNA-seq design.

Current state: prior public-final source-gated QA placeholder rejected.

Required change:

- use an audited lifespan/context source, or
- use a compact source-cited intervention schematic;
- never fake a survival curve;
- say CR, not starvation;
- specify glucose only where needed;
- source fence remains total/rRNA-depleted JM105.

## Panel B — hero age × CR state-space

Claim: CR suppresses a defined age-linked NMD-hidden retained-intron state in old cells.

Evidence: aging effect versus old-cell CR suppression for strict eligible introns.

Required change:

- use `pass_strict_nuclear_orf_gate` for the eligible universe;
- use explicit candidate/gate columns rather than recomputing a loose threshold-only set;
- exclude mitochondrial transcript contamination;
- visible labels must be common names only;
- export systematic IDs and exact matched aliases only in TSV/provenance;
- retain a dedicated right-side label lane and no label–point overlap.

## Panel C — compact definition inset

Claim: aging effect and CR suppression define the target-set state space.

Required change:

- compact definition inset, not an equal-size dashboard panel;
- dedicated top title/descriptor lane;
- dedicated plot lane;
- dedicated bottom descriptor and footer lanes;
- no clipped left/right descriptors;
- no focus box overlapping the bottom descriptor;
- show `candidate_score = min(aging_effect, CR_suppression)` as selection logic, not as a biological effect.

## Panel D — ranked named candidates

Claim: the strongest CR-suppressed aging introns are real named genes, not anonymous points.

Required change:

- rerank only after the corrected nuclear candidate set is locked;
- no mitochondrial transcript rows;
- common gene names only on the visible panel;
- systematic IDs only in audit/provenance;
- dedicated left label lane and ranked-effect plot lane;
- avoid duplicated labels.

## Panel E — raw NMD-on/off profiles

Claim: raw matched NMD-on/off condition profiles support the computed NMD-hidden CR suppression.

Required change:

- source-lock the raw condition table before rendering;
- fail closed if raw IR columns are unavailable;
- do not render blank axes or an empty legend;
- separate subplot title, legend, x-tick, group-label, and footer lanes;
- code comment must state `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`;
- matched conditions: young 2%, old 2%, old 0.1% CR, with NMD-on and NMD-off shown honestly.

## Panel F — informative validated gate transitions

Claim: gate hierarchy distinguishes the eligible universe, aging-linked, CR-suppressed, and locked candidate sets.

Required change:

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
