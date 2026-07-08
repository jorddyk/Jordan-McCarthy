# Code handoff — 2026-07-08 — Intronsaurus v3I helper backfill

## Repo

`jorddyk/Jordan-McCarthy`

## Project area

`projects/jm105-intronsaurus/intronsaurus-browser/`

## Human purpose

Recover useful operational code from the current JM105/Intronsaurus Explore-tab restoration work and place it in the private GitHub repo under a project-first path.

## Files created

- `projects/jm105-intronsaurus/intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch`
- `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh`

## Files updated

- `projects/jm105-intronsaurus/intronsaurus-browser/README.md`
- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Files deliberately not committed

- `Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip` — archive/bundle, not a canonical text source file.
- Generated HTML/tar.gz/checksum outputs — generated artifacts, not source.
- Raw sequencing data, BAM/BAI/SAM/CRAM/FASTQ files, Slurm logs — excluded by repo rules.
- Large Python builder `127_intronsaurus_explore_restored_DATA_fix_v3I.py` — exact full source recovered in sandbox, but not yet imported as text source in this pass; kept as explicit recovery target because the v3I helper scripts are not standalone without it and prior patch-chain dependencies.

## Scientific/data status

No fake biological data were generated or committed. The helper scripts operate on real JM105/JM101 files already on Euler and are administrative wrappers only.

## Implementation notes

The v3I fix addressed a JavaScript data-access bug in the Explore tab: the old working Explore graph data lived in lexical `DATA.explorePanels`, while an earlier patch tried to read `window.DATA`, causing empty graphs/categories. The imported helpers preserve the v3I operational workflow without committing generated browser outputs.

## Final code paths

```text
projects/jm105-intronsaurus/intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch
projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1
projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1
projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh
```

## Legacy-backfill progress

Recovered and imported exact helper scripts for the active Intronsaurus v3I repair path. Updated docs to mark the larger Python builder and JM101/JM105 STAR/integration scripts as exact-source recovery targets still needing text import.

## Remaining source-recovery targets

- `127_intronsaurus_explore_restored_DATA_fix_v3I.py`
- `110_JM101_JM105_integrate_intronsaurus.py`
- `113_JM101_STAR_align_array_LOAD_STACK.sbatch`
- `114_JM101_integrate_after_STAR_LOAD_STACK.sbatch`
- full ImageJ/Fiji aging-chip macros
- complete language-learning HTML apps
