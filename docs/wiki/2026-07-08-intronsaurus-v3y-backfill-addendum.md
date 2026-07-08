# Intronsaurus vNext3Y Backfill Addendum

Date: 2026-07-08

## Canonical status

The current canonical Intronsaurus Sun proteomics target is vNext3Y: single-entry Gene Stories with no right-side gene panel, comparison-matched JM105 RNA/rRNA-depleted evidence and Sun et al. 2021 protein-abundance evidence, common-name mapping, and explicit RNA-vs-protein labeling.

## Imported paths

```text
projects/jm105-intronsaurus/intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch
projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1
projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1
projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh
projects/jm105-intronsaurus/intronsaurus-browser/README.md
```

## Still pending

```text
projects/jm105-intronsaurus/intronsaurus-browser/integrate-sun-matched-rna-protein-gene-stories.py
```

Source clue:

```text
/mnt/data/Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle/141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py
```

Status: exact full source recovered in the active sandbox, but full text-source import is still pending. Do not reconstruct it from summary.

## Files deliberately not committed

- Sun workbook `11357_2021_412_MOESM3_ESM.xlsx`
- generated HTML
- tar.gz archives
- Slurm logs
- raw sequencing or mass-spec files
- intermediate v3P-v3X attempts

## Scientific guardrails

- Keep RNA/host transcript abundance distinct from protein abundance.
- Do not call CR starvation.
- Do not generate fake biological data.
- Figure 2 remains total/rRNA-depleted only unless explicitly changed.
