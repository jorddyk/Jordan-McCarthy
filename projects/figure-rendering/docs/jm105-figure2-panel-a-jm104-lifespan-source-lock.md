# JM105 Figure 2A — JM104 lifespan source lock

Date locked: 2026-07-14

## Panel identity

Figure 2A is the replicative-lifespan/survival panel establishing caloric restriction as the lifespan-extending entry point. It is not an RNA-seq condition schematic and must not be replaced by one without Jordan's explicit approval.

## Canonical source

Windows path supplied by Jordan:

```text
Y:\for Yves\Jordan\Spliceosome Shift CR Paper\Figure 2\Panel2A_Jm104_AnalysisJordan.xlsx
```

Workbook sheet:

```text
JM104_AnalysisJordan
```

Relevant columns:

```text
Image Path
Position
Genotype
% Glucose
RLS
Died in chip 0-no 1-yes
Frame at death
```

## Verified source facts

- Total mother cells: 150.
- 2% glucose control: n = 52.
- 0.5% glucose CR: n = 98.
- The event/censor field is `Died in chip 0-no 1-yes`; blank values are treated as censored rather than silently converted to deaths.
- A two-group log-rank calculation from the workbook reproduces the current panel statistic: `p = 0.0005499800547840875`, displayed as `5.50 × 10^-4` or `5.50e-04`.
- The panel must be rendered from these cell-level values. Do not reconstruct survival values from the current raster composite.

## Required visible content

- Survival probability y-axis.
- Replicative lifespan in divisions x-axis.
- 2% glucose control cohort label with n = 52.
- 0.5% glucose CR cohort label with n = 98.
- Log-rank p value derived from the workbook.
- Nature Aging-compatible restrained survival curves and confidence intervals.

## Output contract

The Figure 2 renderer must produce Panel A together with Panels B-F whenever Jordan requests the complete Figure 2. Required outputs are fixed-dimension transparent SVG, PDF, PNG, white preview PNG, source TSV, statistics TSV, and render audit. No automatic tight cropping. SVG text remains editable.

## Anti-drift rule

The availability of an easier schematic or previously recovered panel is never a reason to substitute Panel A's biological identity. When this workbook is available, a source-gated placeholder is no longer acceptable for Figure 2A.
