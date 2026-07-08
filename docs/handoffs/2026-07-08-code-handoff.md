# CODE HANDOFF — 2026-07-08

## Repo

`jorddyk/Jordan-McCarthy`

## Branch name

`main`

## PR title

No PR opened. Safe Markdown updates and one small canonical JM105 analysis script were committed directly to `main`.

## Project area

Primary: JM105 / Intronsaurus.

Secondary documentation touched: figure rendering and global code wiki.

## Human purpose

Begin the one-time legacy code backfill by importing exact usable code where full source was available and documenting source-recovery targets where only summaries, filenames, or partial snippets were found.

## Files created/updated

Created:

- `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py`

Updated:

- `projects/README.md`
- `projects/jm105-intronsaurus/README.md`
- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`
- `projects/figure-rendering/docs/legacy-code-backfill.md`
- `docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
- `docs/handoffs/2026-07-08-code-handoff.md`

## Files deliberately not committed

- Raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, ND2, TIFF, archives, SLURM logs, scratch folders, generated plots, Excel workbooks, PowerPoint/Word manuscript artifacts, and output tarballs.
- ImageJ/Fiji/Groovy macros whose exact complete source was not recovered.
- Language-learning HTML apps whose full `<!DOCTYPE html>` to `</html>` source was not recovered.
- Intronsaurus reader bundles where only archive names/source clues were available.
- Reconstructed versions of older Rsubread/STAR/IRFinder scripts where only provenance summaries were found.

## Scientific/data status

The imported JM105 determinant script uses real JM105 Euler-side tables as inputs. It does not generate fake biological data. It preserves the working interpretation that RNA-seq currently supports selective NMD-revealed intron leakage, not a global all-intron burden claim.

## Implementation notes

The imported script classifies old-selective leaky introns using the detector logic:

```text
Old detector   = Old upf1Δ - Old WT
Young detector = Young upf1Δ - Young WT
Old-selective leakage = Old detector - Young detector
```

It then compares functional modules and splice-architecture features including 5′ splice site, branchpoint, branchpoint-to-3′SS spacing, 3′ splice site, and polypyrimidine-tract features.

GitHub connector status:

- Repository resolved: `jorddyk/Jordan-McCarthy`
- Visibility: private
- Permissions: admin/push available
- Default branch: `main`

## Final code paths

```text
projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py
```

## Legacy-backfill progress

Recovered and committed one canonical JM105 analysis script. Updated the recovery queues with specific next targets:

```text
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
scripts/29_old_cell_leaky_intron_determinants.py original SVG-rich Euler draft
```

Older high-priority unrecovered targets remain:

```text
110_JM101_JM105_integrate_intronsaurus.py
111_JM101_STAR_align_array.sbatch
112_JM101_integrate_after_STAR.sbatch
JM101 Rsubread Step 2/3 scripts
JM101 IRFinder draft workflow
Intronsaurus vNext3 / vNext3AE reader bundles
JM128/JM129 Fiji/Groovy microscopy scripts
language-learning active-recall HTML apps
personal intelligence agency prompts/rubrics
```

## Code-focused self-counterintelligence

Detected risk: the repo can become a graveyard of daily logs instead of a useful human codebase.

Containment action: this handoff updated project folders and the wiki first; the handoff log records what changed but is not the primary code location.
