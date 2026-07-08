# Jordan McCarthy Code Wiki

_Last updated: 2026-07-08 Europe/Zurich_

## Repository purpose

This private repository is the canonical code vault for Jordan McCarthy's ChatGPT-assisted code, analysis, figure-rendering workflows, and reproducibility handoffs.

Canonical repository: `jorddyk/Jordan-McCarthy`

## Operating rules

1. Preserve only clean, useful, most-current code.
2. Do not preserve intermediate attempts, duplicate scratch scripts, or one-off failed variants.
3. Prefer updating canonical files over creating new files.
4. Never generate fake biological data.
5. If an experiment has not been done, outputs must clearly say `NO DATA`.
6. Distinguish real data, simulated toy data, and `NO DATA` placeholders.
7. Do not commit raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, archives, SLURM logs, scratch folders, cache folders, temporary renders, or Euler output clutter.
8. Do not commit duplicate files named like `final.py`, `final_final.py`, `test.py`, `newplot.py`, `v2_fixed.py`, or `chatgpt_version.py`.

## Current project areas

### JM105 / Intronsaurus

Status: active project context, but no canonical runnable analysis script was verified for commit in the 2026-07-08 handoff.

Known constraints:

- Figure 2 should be redesigned around total/rRNA-depleted data only unless Jordan explicitly changes this.
- Poly-A data should not be used or shown for Figure 2 unless explicitly restored by Jordan.
- Figure panels or experiments not yet done must be marked `NO DATA`.
- Distinguish NMD-off/upf1D raw retained signal from NMD-hidden off-minus-on signal.
- Avoid unsupported claims that caloric restriction equals starvation.
- For gene stories, distinguish RNA/host transcript abundance from protein abundance.

### Figure rendering / manuscript mockups

Status: active, but no canonical script verified for commit in this handoff.

Known constraints:

- Do not fake data.
- Preserve original panel aspect ratios unless Jordan explicitly allows resizing.
- Match Nature Aging-style storytelling while remaining Yves-compatible.
- Use existing figure panels where possible; clearly label newly required panels.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.

### Code handoff workflow

Each handoff should include:

- Repo
- Branch name
- PR title
- Commit message
- Files to create/update
- Files not to commit
- Scientific/data status
- Implementation notes
- Final code

## Last-known canonical handoff decisions

### 2026-07-08

- Repository confirmed: `jorddyk/Jordan-McCarthy`
- Repository visibility: private
- GitHub permissions: admin/push available through connector
- Repo was initially empty at time of bootstrap
- Created this wiki as the initial canonical code-governance document
- No runnable analysis code committed because no clean, verified canonical code was identified in the current run

## Open risks / self-counterintelligence

Current code-focused internal risk: code and figure-generation context is spread across chats, Drive artifacts, and task prompts rather than a single repository structure.

Containment action: use this wiki as the single source of truth for canonical code status and update it only from verified handoff content.
