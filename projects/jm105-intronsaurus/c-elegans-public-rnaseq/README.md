# JM105–C. elegans public RNA-seq triangulation

Complete Euler workflow for testing whether public *C. elegans* RNA-seq shows
aging-, dietary-restriction-, and NMD-associated retained-intron patterns related
to JM105.

Pipeline version: `2026-07-22.3`.

## Scientific design

No public worm study contains the complete JM105 factorial of age × dietary
restriction × NMD state × RNA-processing genotype. The workflow therefore keeps
five studies separate and triangulates related questions without subtracting
values across studies.

| Role | Accession | Prespecified comparison |
|---|---|---|
| Primary dietary restriction × NMD | `SRP089617` | WT and `eat-2` worms under control or `smg-2` RNAi at adult day 1; separate baseline WT versus `eat-2`; separate adult-day-3 `hrpu-1` RNAi test |
| NMD × reduced insulin/IGF signalling | `GSE94077` | N2, `smg-2`, `daf-2`, and `daf-2;smg-2` at adult day 1 |
| Direct SMG-2 association | `GSE100929` | N2 input, `smg-1` input/IP, and `smg-1;smg-2` input/IP negative control |
| Adult-aging bridge | `GSE124994` | replicated adult days 1–10 in `fem` and `gem` sterile strains |
| Independent genetic dietary restriction | `GSE240821` | exact-GSM allowlist for N2 EV, `eat-2` EV, `eat-2 + daf-16 RNAi`, `eat-2 + pha-4 RNAi`, and `eat-2;mxl-2` EV |

The manifest gate runs before reference construction or FASTQ download. If a
prespecified group cannot be resolved, the driver exits and writes an audited
failure report rather than manufacturing a contrast.

## Closest JM105-like comparison

For `SRP089617`:

```text
NMD_hidden in WT
= IR(WT + smg-2 RNAi) - IR(WT + control RNAi)

NMD_hidden in eat-2
= IR(eat-2 + smg-2 RNAi) - IR(eat-2 + control RNAi)

DR-by-NMD comparison
= NMD_hidden in eat-2 - NMD_hidden in WT
```

This resembles the JM105 comparison of matched NMD-off minus NMD-on under normal
versus CR conditions. It differs because `eat-2` is chronic genetic restriction
of pharyngeal pumping and `smg-2` is reduced by RNAi, whereas JM105 uses low
glucose and `upf1Δ`.

## Definitions and interpretation boundaries

- `JM105_IR = (EI + IE) / ((EI + IE) + 2 × EE_total)`.
- `NMD_hidden = IR(NMD off) − IR(matched NMD on)`.
- `candidate_score = min(aging_effect, CR_suppression)` is preserved as a JM105
  definition but is not used because the full factorial is unavailable.
- EI and IE require one contiguous aligned block spanning the relevant boundary
  by at least 8 aligned bases on each side.
- EE_total requires an exact CIGAR `N` match to the annotated intron.
- Counts are unique query-name counts after query-name sorting.
- `eat-2` is genetic dietary restriction caused by reduced pharyngeal pumping.
- `daf-2` is reduced insulin/IGF signalling, not caloric restriction.
- SMG-2 IP supports RNA association; it does not establish cytoplasmic export or
  translation.
- None of these datasets alone proves cytoplasmic pre-mRNA leakage.
- Studies are analysed separately. Values are never subtracted across studies.

## Reference and sequencing treatment

The workflow uses Ensembl release 113, WBcel235. One representative
protein-coding transcript is selected per gene by longest CDS, then exonic
length and genomic span. Introns shorter than 30 bp are excluded.

The run manifest records SRA library selection, layout, platform, instrument,
read count and base count. Technical runs sharing one public biological-sample
identifier are summed before IR is calculated. Biological replicates remain
separate.

## Figure lane map

Every rendered object is assigned exactly once.

| Object | Lane | Coordinate / anchor |
|---|---|---|
| Primary DR × NMD title | descriptor/title | top-left of primary axes |
| Primary biological-sample points | plot | primary data rectangle |
| Primary group names | x-tick | primary bottom axis |
| Primary interaction estimate | right-stat | primary upper-right axes anchor |
| Aging title | descriptor/title | top-left of aging axes |
| Aging points and fitted lines | plot | aging data rectangle |
| Aging sterile-strain key | legend | aging legend region |
| Adult-day values | x-tick | aging bottom axis |
| Aging metric | label | aging left axis |
| DR-replication title | descriptor/title | top-left of effect axes |
| DR effect estimates and intervals | plot | effect data rectangle |
| Study names | group label | effect y-tick lane |
| Zero reference | plot | x=0 |
| NMD-hidden title | descriptor/title | top-left of NMD axes |
| N2 and `daf-2` distributions | plot | NMD data rectangle |
| Genotype names | x-tick | NMD bottom axis |
| Median interaction | right-stat | NMD upper-right anchor |
| `hrpu-1` title | descriptor/title | top-left of scatter axes |
| DR-effect × `hrpu-1`-effect points | plot | scatter data rectangle |
| rho and p | right-stat | scatter upper-right anchor |
| SMG-2-support title | descriptor/title | top-left of direct-support axes |
| stabilization × enrichment points | plot | direct-support data rectangle |
| support count | right-stat | direct-support upper-right anchor |
| Composite interpretation boundary | footer | dedicated sixth contact-sheet cell |

## Collision inventory

- `[primary interaction text] × [primary points]` → statistic occupies the
  upper-right right-stat lane; rendered extent is checked by the audit.
- `[aging legend] × [aging points]` → legend occupies its own legend region;
  white-preview inspection remains required after real data are rendered.
- `[confidence interval] × [point estimate]` → interval is drawn first and point
  estimate above it.
- `[NMD median text] × [violin]` → statistic occupies the right-stat lane.
- `[hrpu-1 rho/p] × [point cloud]` → statistic occupies the right-stat lane.
- `[SMG-2 support count] × [point cloud]` → statistic occupies the right-stat lane.
- `[composite interpretation] × [data panels]` → interpretation uses a dedicated
  footer cell.
- `[transparent text] × [dark viewer]` → every figure has a white-background
  preview PNG.
- x-tick lane: checked; explanatory prose is not placed in this lane.
- footer lane: checked; it does not share an axes cell.

The renderer writes `FIGURE_AUDIT.md`. It reports anything that cannot be
verified until real data are rendered rather than claiming an unverified pass.

## Render contract

Each panel and the composite use declared fixed canvas dimensions and export:

- transparent SVG with editable text;
- transparent PDF;
- transparent PNG;
- white-background preview PNG.

`bbox_inches="tight"` does not appear in the renderer.

## Job architecture

1. Driver resolves metadata and enforces the manifest gate.
2. Reference job downloads WBcel235/Ensembl 113 and creates the STAR index.
3. Sample array processes one public SRA run per task, with at most four
   concurrent download/alignment tasks.
4. Aggregate job collapses technical runs, computes fixed-universe contrasts and
   renders the figures.

The sample array starts only after the reference succeeds. Aggregation starts
only after all sample tasks succeed.

## Euler submission

Euler compute nodes need the ETH proxy for public downloads. In an Euler login
shell:

```bash
module load eth_proxy
WORM_ROOT=/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS \
CODE_ROOT=/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS/code/JM105_CELEGANS_WORM_ANALYSIS \
ENV_PREFIX=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/software/micromamba-root/envs/jm105-hgps-conservation \
bash "$CODE_ROOT/submit_pipeline.sh"
```

The PowerShell uploader performs the upload, loads `eth_proxy` in a remote Bash
login shell and submits the driver:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\upload_submit_c_elegans_public_rnaseq.ps1
```

Use the exact watcher command printed after submission.

## Outputs

Results are written under:

```text
/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS/work/results
```

Key outputs include `FINAL_REPORT.md`, `FINAL_VERDICT.md`,
`METHODS_JM105_TO_WORM.md`, `CLAIM_BOUNDARIES.md`, `sample_scores.tsv`,
`contrast_summary.tsv`, per-intron contrast tables, `FIGURE_MANIFEST.tsv`,
`FIGURE_AUDIT.md`, `FILE_SHA256.tsv`, and `figures/`.

Raw reads, alignments, STAR indexes, logs, caches, generated results and archives
are deliberately excluded from GitHub.
