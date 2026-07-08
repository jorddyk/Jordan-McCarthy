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

## Legacy helper scripts imported in this pass

These helper scripts came from the current Explore-tab restoration sequence. They are preserved because they capture exact PowerShell/Euler operational commands, but the currently preferred browser source remains the newer vNext3Y workflow above.

| File | Purpose | Status |
|---|---|---|
| `intronsaurus-explore-restored-data-fix-v3i.sbatch` | Euler wrapper for the vNext3I Explore-tab restoration build. | Imported exact helper source; requires the v3I Python builder and legacy patch-chain scripts on Euler. |
| `upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | Uploads the vNext3I bundle and submits the Euler job. | Imported exact helper source. |
| `retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves and opens the completed vNext3I archive from Euler. | Imported exact helper source. |
| `check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks Slurm status and vNext3I stdout/stderr tails. | Imported exact helper source. |

## vNext3I source status

Source clue: `127_intronsaurus_explore_restored_DATA_fix_v3I.py` / `Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip`.

Purpose: restore the original total/rRNA-depleted Explore Introns tab by reading the original lexical `DATA.explorePanels` object, keep category filtering/search/all-introns display, and add poly-A enriched RNA as an additional graph view without touching working tabs.

Status: exact full Python source was recovered in the active project sandbox and packaged for download, but the large Python builder itself still needs a text-source import if this older v3I path is ever needed again. Do not treat the helper scripts above as a standalone rebuild without that Python source and the legacy patch-chain dependencies.

## Scientific/data status

- Uses real JM105 total/rRNA-depleted Intronsaurus input data already present on Euler.
- Uses real Sun et al. 2021 processed proteomics from `11357_2021_412_MOESM3_ESM.xlsx` where the vNext3Y workflow is used.
- Does not commit raw sequencing data, raw mass-spec files, the Sun workbook, generated HTML, tar.gz archives, or Slurm logs.
- Keeps RNA/host transcript abundance distinct from protein abundance.
- Does not call caloric restriction starvation.
- Does not invent missing biological data; unavailable comparisons are labeled as unavailable.

## vNext3Y design decision

The canonical imported version is vNext3Y because it supersedes intermediate v3P-v3X attempts. v3Y keeps Gene Stories as a single main entry with no right-side gene panel, groups comparisons by biological contrast, and shows the matching JM105 RNA/rRNA-depleted and Sun protein-abundance layers together.
