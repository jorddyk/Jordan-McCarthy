# Jordan McCarthy Code Vault

Private, project-organized repository for Jordan McCarthy's useful canonical code.

This repo is not meant to be a chronological dump of ChatGPT outputs. It is organized by **project**, **goal**, and **what the code actually does**.

## Repository map

```text
projects/
  jm105-intronsaurus/
    Purpose: RNA-seq, intron retention, leakage, figure, and manuscript-support code.
  figure-rendering/
    Purpose: figure mockup/rendering workflows and reusable plotting/layout utilities.
  language-learning/
    Purpose: German/TELC active-recall web apps and study tooling.
  personal-intelligence-agency/
    Purpose: scheduled-task prompts, scoring rubrics, and automation support code.

docs/
  wiki/
    Purpose: current source-of-truth notes about canonical code and project status.
  handoffs/
    Purpose: audit trail only. Handoffs are logs, not the main organizing structure.
```

## Current canonical principle

A file belongs in the project folder where a human would look for it later.

Examples:

- A TELC C1 recall app belongs under `projects/language-learning/active-recall-apps/`.
- A JM105 intron-retention analysis script belongs under `projects/jm105-intronsaurus/analysis/`.
- A Nature Aging figure-layout renderer belongs under `projects/figure-rendering/nature-aging-mockups/`.
- A scheduled-task scoring rubric belongs under `projects/personal-intelligence-agency/`.

Daily code handoffs should update the relevant project files and then record what happened in `docs/handoffs/`.

## Hard rules

- Do not commit fake biological data.
- Mark unperformed experiments or panels as `NO DATA`.
- Do not commit raw sequencing data, BAM/SAM/CRAM files, SLURM logs, scratch folders, cache folders, or temporary renders.
- Do not preserve duplicate scratch scripts with names like `final.py`, `test.py`, `newplot.py`, or `v2_fixed.py`.
- Prefer human-readable file names that explain purpose.
