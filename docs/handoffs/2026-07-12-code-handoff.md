# CODE HANDOFF — 2026-07-12

## Repo

`jorddyk/Jordan-McCarthy` — verified private, default branch `main`, authenticated access includes admin and push permissions.

## Project area

`projects/imagej-fiji-aging-chips/`

## Human purpose

Advance the initial legacy backfill for JM076/JM128/JM129 Fiji/ImageJ/Groovy aging-chip and MitoSOX workflows without inventing source code from remembered paths, dimensions, frame ranges, or output filenames.

## Branch name

`main`

## PR title

No PR. Documentation-only recovery-state updates were committed directly to `main`.

## Commit message

- `docs: update ImageJ legacy recovery status`
- `docs: add ImageJ legacy backfill ledger`
- `docs: record 2026-07-12 ImageJ recovery pass`
- `docs: add 2026-07-12 code handoff`

## Project files created/updated

Created:

- `projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md`

Updated:

- `projects/imagej-fiji-aging-chips/README.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Handoff/audit files created/updated

Created:

- `docs/handoffs/2026-07-12-code-handoff.md`

## Files not to commit

- Raw `.nd2` microscopy files.
- TIFF stacks or merged microscopy outputs.
- Generated RLS/ROS image products.
- Scratch exports, temporary images, caches, logs, and archives.
- Plausible reconstructions of JM076/JM128/JM129 scripts made only from workflow summaries.
- Quantitative MitoSOX outputs with silent 8-bit conversion or undocumented auto-contrast.

## Scientific/data status

No new biological data were generated or committed.

No runnable microscopy code was imported. Exact historical workflow clues remain documentation only.

Known quantitative constraints remain active:

- Preserve source bit depth.
- Do not silently convert quantitative MitoSOX data to 8-bit.
- Do not silently auto-contrast quantitative data.
- Make rolling-ball background subtraction explicit, including radius and scope.
- Label display-only contrast separately from quantitative processing.

## Implementation notes

Repository access was verified first. `README.md`, `projects/README.md`, and the code wiki were inspected before project changes.

File Library was searched with focused exact clues:

- `Image001.nd2`
- `Image001_Pos0_Hyperstack.tif`
- `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions`
- `MitosoxRedInducibleFusionsRepeat.nd2`
- `Continue001.nd2`
- `Continue002.nd2`
- `rollingBallRadius=100`
- `C=2`
- `Z=60`
- `T=107/139/145`
- `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif`
- `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif`

The returned files were unrelated scientific documents, posters, a dashboard, the D-BIOL program, and already-known language-learning HTML. None contained a complete `.ijm` or Groovy source body.

Code-focused risk detected: detailed remembered workflow parameters could encourage a plausible reconstruction that differs from the original in frame indexing, channel order, Bio-Formats invocation, bit depth, or saving semantics.

Containment action: `projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md` is now the single source of truth for unrecovered microscopy code and exact import status.

## Final code or candidate imports

Actual canonical code imported: **none**.

Candidate imports still pending exact complete source:

- `projects/imagej-fiji-aging-chips/macros/jm128-split-nd2-positions-bioformats.ijm`
- `projects/imagej-fiji-aging-chips/macros/jm128-extract-mitosox-c2-every6-zpositions.ijm`
- `projects/imagej-fiji-aging-chips/macros/jm128-stitch-image-and-image001-brightfield-rls.ijm`
- `projects/imagej-fiji-aging-chips/macros/jm128-merge-ros-bf-fl.ijm`
- `projects/imagej-fiji-aging-chips/groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`
- JM076 Step 1/2/3/4/6 macros listed in the project backfill ledger.

## Legacy-backfill progress

ImageJ/Fiji legacy recovery is now represented by a project-local backfill ledger rather than only the global wiki or remembered conversation context.

Progress this run:

- Converted the JM076/JM128/JM129 recovery queue into a structured project-level ledger.
- Recorded exact search keys and search-result classification.
- Confirmed that no exact full runnable source was recovered in accessible File Library results.
- Prevented partial snippets or reconstructed code from being mislabeled as canonical.

Next legacy passes should continue with distinct source surfaces or exact filename searches rather than repeating this same File Library query set unchanged.
