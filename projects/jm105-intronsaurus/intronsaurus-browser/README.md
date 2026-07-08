# Intronsaurus browser

Human purpose: preserve canonical code for the interactive JM105/JM101 Intronsaurus browser and its Gene Stories layer.

## Canonical imported workflow

| File | Purpose | Status |
|---|---|---|
| `integrate-sun-matched-rna-protein-gene-stories.py` | Builds Intronsaurus vNext3Y from the precise v3M base and integrates Sun et al. 2021 MOESM3 protein-abundance comparisons into single-entry Gene Stories. | Exact source recovered from the vNext3Y code bundle and imported. |
| `run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | Euler Slurm wrapper for the vNext3Y build. | Exact source recovered and imported. |
| `upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | Windows helper to upload the builder, source archive, Sun workbook, and status checker to Euler and submit the job. | Exact source recovered and imported. |
| `retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | Windows helper to retrieve vNext3Y HTML, validation, tables, and archive from Euler. | Exact source recovered and imported. |
| `check-intronsaurus-matched-rna-protein-gene-stories.sh` | Safe Euler status checker for the vNext3Y job. | Exact source recovered and imported. |

## Scientific/data status

- Uses real JM105 total/rRNA-depleted Intronsaurus input data already present on Euler.
- Uses real Sun et al. 2021 processed proteomics from `11357_2021_412_MOESM3_ESM.xlsx`.
- Does not commit raw sequencing data, raw mass-spec files, the Sun workbook, generated HTML, tar.gz archives, or Slurm logs.
- Keeps RNA/host transcript abundance distinct from protein abundance.
- Does not call caloric restriction starvation.
- Does not invent missing biological data; unavailable comparisons are labeled as unavailable.

## vNext3Y design decision

The canonical imported version is vNext3Y because it supersedes intermediate v3P-v3X attempts. v3Y keeps Gene Stories as a single main entry with no right-side gene panel, groups comparisons by biological contrast, and shows the matching JM105 RNA/rRNA-depleted and Sun protein-abundance layers together.
