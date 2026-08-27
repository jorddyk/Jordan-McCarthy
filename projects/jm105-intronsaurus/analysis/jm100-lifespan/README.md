# JM100 lifespan preprocessing

`JM100_lifespan_to_csv_20260728.py` converts the real JM100 replicative-lifespan workbook into the three-column CSV consumed by lifespan panels: `genotype`, `glucose`, and `divisions`.

The script is intentionally separate from figure rendering because it performs source cleaning and design validation:

- uses one row per mother cell and the `Buddingcount` lifespan endpoint;
- explicitly maps workbook `Mud1` labels to `mud1Δ`;
- checks for unrecognized strain and glucose values and fails closed;
- detects the transposed 2% versus 0.5% labels in the workbook’s `Graphs` summary sheet;
- preserves the fact that JM100 uses 0.5% glucose whereas the JM105 RNA-seq CR arm uses 0.1%;
- reports group sizes, medians, means, maxima, Mann–Whitney tests, and the difference in CR effects between genotypes.

No workbook or biological output data are committed here. The script passed `python -m py_compile` before import.
