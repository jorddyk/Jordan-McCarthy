# Code handoff — JM105 C. elegans public RNA-seq v3

## Source searched

- the complete original worm workflow bundle;
- the complete manifest-v2 replacement sources;
- the exact manifest-v3 GSE240821 repair script;
- Euler driver, manifest-gate and Slurm status output supplied by Jordan;
- the repository README and Code Wiki operating rules;
- draft PR #6, the current metazoan-conservation branch.

## Canonicalization result

The complete most-current workflow is canonicalized at:

```text
projects/jm105-intronsaurus/c-elegans-public-rnaseq/
```

The project contains the full Python, Slurm, Bash and PowerShell workflow. One
canonical v3 source replaces the temporary v1/v2/v3 patch sequence. The patch
bundles themselves are not committed.

## Scientific design retained

- five public studies remain separate;
- `NMD_hidden = IR(NMD off) - IR(matched NMD on)` is computed only for matched
  groups within one study;
- `candidate_score = min(aging_effect, CR_suppression)` is documented but not
  used without the full JM105 factorial;
- `eat-2` is genetic dietary restriction;
- `daf-2` is reduced insulin/IGF signalling, not CR;
- SMG-2 IP is association evidence, not proof of export or translation;
- no cross-study subtraction is used to manufacture missing experimental cells.

## Runtime provenance

- final pipeline version: `2026-07-22.3`;
- metadata gate: passed;
- driver `8176077`;
- reference `8176647`;
- sample array `8176648`, 158 tasks, maximum four concurrent;
- aggregate `8176649`.

At canonicalization time, the reference was running and dependent jobs were
pending. No generated biological result was available or imported.

## Validation

- all Python files compiled successfully;
- all Bash/Slurm files passed `bash -n`;
- source SHA-256 manifest regenerated;
- renderer retains fixed dimensions, editable SVG text, transparent SVG/PDF/PNG,
  white-background previews and no `bbox_inches="tight"`;
- raw sequencing, alignments, indexes, logs, caches, archives, compiled files and
  generated figures/results remain excluded.
