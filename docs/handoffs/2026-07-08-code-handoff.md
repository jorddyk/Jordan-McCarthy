# CODE HANDOFF — 2026-07-08

## Repo

`jorddyk/Jordan-McCarthy`

## Branch name

`main`

## PR title

No PR opened. Safe Markdown updates, exact prompt/spec artifacts, interpretation summary, and previously recovered small canonical scripts were committed directly to `main`.

## Project area

Primary: JM105 / Intronsaurus.

Secondary: figure rendering / Nature Aging mockups; personal intelligence agency prompt management; global code wiki.

## Human purpose

Continue the one-time legacy code backfill by importing exact reusable project assets where full text was available and documenting source-recovery targets where only summaries, filenames, or partial snippets were found.

## Files created/updated

Created in earlier pass:

- `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py`

Created in this pass:

- `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md`
- `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md`
- `projects/jm105-intronsaurus/docs/what-data-shows-summary.md`
- `projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md`

Updated across the 2026-07-08 passes:

- `projects/README.md`
- `projects/jm105-intronsaurus/README.md`
- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`
- `projects/figure-rendering/README.md`
- `projects/figure-rendering/docs/legacy-code-backfill.md`
- `projects/personal-intelligence-agency/README.md`
- `docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
- `docs/handoffs/2026-07-08-code-handoff.md`

## Files deliberately not committed

- Raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, ND2, TIFF, archives, SLURM logs, scratch folders, generated plots, Excel workbooks, PowerPoint/Word manuscript artifacts, and output tarballs.
- ImageJ/Fiji/Groovy macros whose exact complete source was not recovered.
- Language-learning HTML apps whose full `<!DOCTYPE html>` to `</html>` source was not recovered.
- Intronsaurus reader bundles where only archive names/source clues were available.
- Reconstructed versions of older Rsubread/STAR/IRFinder scripts where only provenance summaries were found.
- Runnable Figure 5 renderer code, because the available source was an exact prompt/spec, not the generated PowerShell/Bash/Python itself.

## Scientific/data status

The imported JM105 determinant script uses real JM105 Euler-side tables as inputs. It does not generate fake biological data. It preserves the working interpretation that RNA-seq currently supports selective NMD-revealed intron leakage, not a global all-intron burden claim.

The newly imported prompt/spec and interpretation Markdown files are not biological data and are not runnable code. They preserve exact workflow/scientific constraints, including: no fake data; `NO DATA — experiment pending` for missing experiments; Figure 2 total/rRNA-depleted-only unless explicitly changed; no unsupported poly-A/P-versus-T/mRNA-like/P−T additions; RNA abundance distinguished from protein abundance; CR not called starvation.

## Implementation notes

The imported JM105 determinant script classifies old-selective leaky introns using the detector logic:

```text
Old detector   = Old upf1Δ - Old WT
Young detector = Young upf1Δ - Young WT
Old-selective leakage = Old detector - Young detector
```

It then compares functional modules and splice-architecture features including 5′ splice site, branchpoint, branchpoint-to-3′SS spacing, 3′ splice site, and polypyrimidine-tract features.

The imported Figure 5 render prompt preserves the required rendering contract: lane map before code, collision inventory before patching, data-provenance manifest, fixed 13.333333 × 7.5 inch canvas, transparent SVG/PDF/PNG plus white-preview PNG, editable SVG text, and no `bbox_inches="tight"`.

GitHub connector status:

- Repository resolved: `jorddyk/Jordan-McCarthy`
- Visibility: private
- Permissions: admin/push available
- Default branch: `main`

## Final code / prompt paths

```text
projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py
projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md
projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md
projects/jm105-intronsaurus/docs/what-data-shows-summary.md
projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md
```

## Legacy-backfill progress

Recovered and committed one canonical JM105 analysis script in an earlier pass. In this pass, recovered and committed exact prompt/spec artifacts and a scientific interpretation summary, without pretending they are runnable code.

Updated the recovery queues with specific next targets:

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
personal intelligence agency prompts/rubrics beyond the legacy-code-backfill prompt
runnable Figure 5 PowerShell/Bash/Python renderer source
JM134 beta-binomial / final layout repair scripts
JM133 weak-5SS/Mud1 source from Euler
```

## Code-focused self-counterintelligence

Detected risk: the repo can become a graveyard of daily logs and prompt artifacts instead of a useful human codebase.

Containment action: prompt/spec artifacts were saved only when exact and reusable, clearly marked non-runnable, and placed under project-purpose folders. Missing source remains in recovery docs rather than being reconstructed.
