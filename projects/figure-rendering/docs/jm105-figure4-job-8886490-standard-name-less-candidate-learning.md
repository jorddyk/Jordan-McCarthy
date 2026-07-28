# JM105 Figure 4 job 8886490: standard-name-less candidate learning

## Observation

Euler job 8886490 failed before rendering because candidate `intron_00064` belongs to `YDL012C`, which has no SGD standard gene name. The renderer had correctly prohibited reader-facing systematic ORF IDs but incorrectly treated every standard-name-less verified ORF as invalid biology.

## Violated invariant

No biological candidate may be removed or renamed merely to satisfy a display-label rule. Reader-facing labels must be truthful, while machine-readable provenance must retain the systematic identifier.

## Permanent correction

1. Separate `gene` (official standard name, blank when none exists), `systematic_gene`, and `display_gene`.
2. Preserve systematic identifiers in exported tables.
3. Use a curated descriptive display-label registry for verified standard-name-less candidates.
4. Current registry: `YDL012C -> Unnamed CYSTM-module protein`.
5. Fail closed for any future candidate that has neither a standard name nor a curated descriptive label.
6. Regression-test the real R64-5-1 GFF mapping before Slurm submission.
7. Treat Slurm failure as terminal; do not continue into retrieval or print success messages.
8. Convert possibly empty native-command output to a string before trimming in PowerShell.

## Status

The v2 candidate renderer and runner were built locally and passed Python compilation, Bash syntax validation, and a targeted standard-name-less-label regression test. They are not canonical until the real Euler run completes, is retrieved, and is visually accepted by Jordan.
