# Projects

This folder is the human-facing organization layer of the repository.

Each project folder should answer four questions:

1. What is this project trying to accomplish?
2. What code is canonical right now?
3. What inputs does the code require?
4. What outputs does it produce?

Daily handoffs may cite these files, but the code itself should live here, not inside date-stamped folders.

## Project folders

| Folder | Human title | Purpose |
|---|---|---|
| `jm105-intronsaurus/` | JM105 / Intronsaurus analysis | RNA-seq, intron retention, leakage, NMD, Mud1/CR, manuscript-support code |
| `figure-rendering/` | Figure rendering and manuscript mockups | Figure-layout scripts, plotting utilities, Nature Aging-style mockups |
| `imagej-fiji-aging-chips/` | ImageJ / Fiji aging-chip macros | Fiji/ImageJ/Groovy macros for aging-chip, MitoSOX, ROS, BF/FL, ND2 splitting, stitching, and quantitative microscopy workflows |
| `language-learning/` | Language-learning apps | German/TELC active-recall apps and study tools |
| `personal-intelligence-agency/` | Personal intelligence agency | Scheduled-task prompts, scoring rubrics, and automation support |
| `rongorongo/` | Rongorongo decipherment | Statistical/computational cryptanalysis of the Rongorongo script: reproduction scripts, blind-coding validators, and null-result adjudication records |

## Backfill rule

Canonical runnable code goes under a project folder with a descriptive path. Daily handoffs and source-recovery notes go under `docs/` and are audit logs only.

## Scientific integrity rules for JM105 / Intronsaurus

- Figure 2 uses total/rRNA-depleted JM105 only unless Jordan explicitly restores another subset.
- Poly-A, P-versus-T, mRNA-like, and P−T constructs are out of Figure 2 unless explicitly restored.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.
- Do not claim caloric restriction is starvation.
- Never generate fake biological data. Missing experiments remain `NO DATA` or documentation-only targets.

## Microscopy integrity rules

- Do not commit raw ND2 or TIFF stacks.
- Do not silently convert quantitative microscopy to 8-bit.
- Do not silently apply auto-contrast to quantitative data.
- Document channel, Z, T, frame sampling, background subtraction, and output naming.
