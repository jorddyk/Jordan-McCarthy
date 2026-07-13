# Figure 4G development lessons — predicted splice-signal accessibility

Date: 2026-07-13  
Project: JM105 / Intronsaurus / Figure 4  
Panel: Figure 4G, predicted splice-signal accessibility

This file records what was learned while adding a secondary-structure/accessibility panel to the Figure 4 architecture story. It is intentionally a lessons/provenance document, not a rendered figure archive.

## Biological question

The initial idea was to ask whether predicted intron secondary structure explains any of the observed Mud1/U1/aging/CR effects. The useful framing became narrower:

> Do locked Figure 4 Mud1/CR-sensitive introns differ because their splice-recognition elements are predicted to be less accessible in folded intron RNA?

That is stronger than a vague “introns have secondary structure” panel because spliceosome biology cares about accessibility of the 5′ splice site, branchpoint, and 3′ splice-site region.

## Preferred ideal method

The ideal method for a final reviewer-grade version is ViennaRNA `RNAplfold` local ensemble unpaired probabilities, optionally with `RNAfold -p` partition-function/base-pair-probability audits.

Planned metrics:

```text
5SS_accessibility = mean P(unpaired) across 5′ splice-site window
BP_accessibility = mean P(unpaired) across branchpoint window
3SS_accessibility = mean P(unpaired) across 3′ splice-site window
splice_signal_occlusion = mean(1 - accessibility across 5SS/BP/3SS)
MFE_per_nt = RNAfold MFE / sequence length
```

## What actually worked on Euler

Euler did not have `RNAfold`, `RNAplfold`, a `ViennaRNA` module, or conda/mamba/micromamba in the active path. A broad filesystem search was too slow and was abandoned. The working dependency solution was:

```bash
module load fast_python_workshop_cpu/2025.0.0
venv_cpu_init
python3 -m pip install --target vendor_py --upgrade ViennaRNA
export PYTHONPATH="$RUN_DIR/vendor_py:$PYTHONPATH"
python3 - <<'PY'
import RNA
print(RNA.fold("GCGCAAAAGCGC"))
PY
```

This uses the Python ViennaRNA/RNAlib binding. The current stored pipeline therefore computes an **MFE-derived accessibility proxy** from `RNA.fold()` dot-bracket output, not RNAplfold ensemble accessibility.

## Failure and repair ledger

| Failure / observation | Cause | Repair / permanent lesson |
|---|---|---|
| `RNAfold` and `RNAplfold` not found | No ViennaRNA CLI/module in current Euler stack | Use Python `ViennaRNA` package installed to local `vendor_py`; do not keep searching `/cluster/project`. |
| PowerShell diagnostic failed on `$(date -Is)` | PowerShell evaluated the Bash expression locally as `Get-Date -Is` | Write diagnostic/run scripts as actual `.sh` files and upload; avoid fragile inline nested heredocs. |
| Rescue script appeared frozen for minutes | It was doing broad `find` across cluster filesystems | Never run broad `find` over `/cluster/project` or `/cluster/software` from an interactive render rescue. Use `module spider`, `command -v`, or targeted search. |
| Architecture table chosen but no sequence column | Table had BP/intron geometry but not sequence | Separate architecture source discovery from sequence discovery. |
| No real sequence table discovered | JM105/Fig4 tables did not carry full intron sequences | Extract intron sequences from FASTA/GFF annotation. |
| Broad Figure 2 `candidate_passed` gave n=59 | Figure 2 broad candidate-pass logic is not the locked Figure 4 selected set | Selected group must come only from locked Figure 4 selected TSV, expected n=49. Figure 2 is used only for pass_age_gate/aging_effect/CR_suppression annotation. |
| Initial effect-size-only panel looked too abstract | Effect-size dots hide whether `ns` means overlap or low power | Final visual shows all introns as small dots plus medians/IQR. |
| Label spills and footer clipping | y-axis labels and long footer text used plot/canvas edges | Move labels to a dedicated left label lane; shorten footer. |
| Visual row order did not match legend | Offsets placed Mud1/CR visually above background | Final row order within each metric follows legend: Background top, Aging-only middle, Mud1/CR bottom. |

## Final grouping rule

The final stored code uses:

```text
selected = locked Figure 4 selected source only, expected n=49
background_pool = locked Figure 4 clean spliceosomal background source, expected n=232
aging_only = background_pool rows with Figure 2 pass_age_gate == true
background = background_pool rows with Figure 2 pass_age_gate == false
```

The successful audit from the development pass had:

```text
Background n=217
Aging-only n=15
Mud1/CR n=49
Total n=281
```

## Final visual design rule

For this panel, use individual dots plus median/IQR rather than an effect-size-only summary.

```text
small dots = individual introns
large dots = group median
bars = IQR
x-axis = within-metric percentile
right stat lane = A/bg and M/A q-value labels
```

The within-metric percentile scale was chosen because accessibility metrics and folding-strength metrics are on different raw units. Raw values are exported and should be used for exact interpretation.

## Interpretation guidance

The current result is best interpreted as:

> MFE-derived splice-signal accessibility / folding strength does not obviously explain why the locked Mud1/CR-sensitive introns are selected from the aging-linked intron set.

Safe wording:

```text
Predicted MFE-derived splice-signal accessibility did not distinguish Mud1/CR-sensitive introns from aging-only introns across the tested accessibility/folding metrics.
```

Avoid:

```text
Secondary structure does not matter.
RNA structure is ruled out.
RNAplfold accessibility shows no effect.
```

Those are too strong because the current code uses an MFE-derived proxy rather than ensemble local unpaired probabilities.

## What to upgrade later

A future reviewer-grade upgrade should add one of the following:

1. ViennaRNA CLI `RNAplfold` if available on a proper environment.
2. A micromamba/conda env with `viennarna` CLI tools if Euler permits it.
3. Experimental yeast RNA-structure probing data only if condition/coverage are appropriate.

The panel title/caption should then be changed from “MFE-derived accessibility proxy” to the actual method used.
