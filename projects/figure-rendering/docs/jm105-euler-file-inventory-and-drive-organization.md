# JM105 Euler inventory and Google Drive organization

Date started: 2026-07-14

## Google Drive project hub

Root folder:

```text
JM105 - Intronsaurus & Nature Aging
Folder ID: 1oDh9G56ECZWox1tHWRSIx6sYsg7LKJq-
```

Subfolders:

```text
00 Governance & Acceptance
01 Canonical Render Packages
02 Source Documents & Figure Specs
03 Euler File Inventories
```

The Figure Acceptance Matrix was moved into `00 Governance & Acceptance`. The existing canonical render-package folder was moved into `01 Canonical Render Packages`. The all-figures PowerPoint, Yves flow document, and Panel 2A workbook were copied into `02 Source Documents & Figure Specs`. A persistent native Google Sheet named `JM105 Euler File Inventory` and an initial TSV seed were placed in `03 Euler File Inventories`.

Only clearly identified JM105 assets should be moved automatically. Documents that merely mention JM105 should first be indexed and reviewed so unrelated personal or lab records are not reorganized incorrectly.

## Euler inventory rule

Before major figure work, refresh the inventory of:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq
```

The inventory must contain at least path, byte size, and modification time. Save the resulting TSV in the Drive `03 Euler File Inventories` folder and append the run to the inventory sheet. The historical `all_files.raw.txt` file is a useful seed but not proof of current state.

## Figure 2F seven-gate source

Raw gate table:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_metrics_all.tsv
```

Generator:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/figure2_stage1B_strict_nuclear_orf_gate.py
```

Canonical renderer:

```text
projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py
```

The seven displayed rows are cumulative. Gate 5 maps to both `pass_floor_gate` and `pass_old2_nmd_sensitive_gate`; the script hard-fails unless the complete seven-gate mask exactly equals `candidate_passed_strict` and the final count is 49. It renders all seven n values from the raw 402-row table and writes a refreshed Euler inventory TSV in the same output directory.
