# JM-134: Does aging/CR reuse the starvation splice switch?

Purpose: compare JM105 total RNA-seq splicing-index behavior against the Parenteau/gkaf525 stationary-phase starvation program.

## Scientific question

Do the same introns change splicing during JM105 caloric restriction or replicative aging as during Parenteau stationary-phase starvation, and does Mud1 control those changes in the same way?

## Current result state from project history

- Exact cross-study matching used systematic ORF plus within-gene intron ordinal.
- JM105 total RNA-seq and Parenteau targeted MPE-seq are different assays.
- Low-glucose CR is not identical to 48-hour stationary phase.
- The correct claim is shared intron-response behavior, not identical U1 occupancy or spliceosome remodeling.

### Beta-binomial update

The first JM-134 significance layer used unweighted sample-level log2 mature/premature ratios and produced only one JM105 significant intron-contrast hit at FDR < 0.10.

A count-aware beta-binomial mature-versus-premature model preserved fragment-count precision and recovered 24 JM105 intron-contrast hits at FDR < 0.10.

## Current interpretation

JM105 reuses part of the Parenteau starvation-responsive intron program, but not as one universal switch.

- Young-cell CR showed the clearest reuse of the starvation-responsive intron program.
- Old-cell CR largely lost that coordinated CR response.
- Aging in high glucose weakly resembled starvation.
- Aging in low glucose shifted in the opposite rank direction.
- Mud1 control was context-dependent rather than uniformly conserved.

## Exact source found but not fully imported yet

Local uploaded files found during backfill:

```text
/mnt/data/JM134_matched_splicing_index.py
/mnt/data/JM134_submit_matched_SI.sh
/mnt/data/JM134_rerender_no_overlap.py
/mnt/data/JM134_run_on_Euler.sh
/mnt/data/81_JM134_symlog_clarity_and_notebook.py
```

Exact source embedded in chat history and queued for import:

```text
scripts/79_JM134_audit_and_beta_binomial.py
scripts/80_JM134_apply_beta_binomial_and_rerender.py
scripts/83_JM134_final_guide_repair.py
```

## Files deliberately not committed in initial pass

- PNG/PDF/SVG rendered figures.
- `JM134_Matched_splicing_index.tar.gz` archive.
- Slurm stdout/stderr logs.
- BAM/BAI or other raw/intermediate sequencing files.

## Current import status

Documentation-only folder created. Runnable scripts remain tracked in `docs/legacy-code-backfill.md` until their complete source can be imported without truncation.
