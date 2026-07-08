# CODE HANDOFF — 2026-07-08

## Repo

`jorddyk/Jordan-McCarthy`

## Branch name

`main`

## PR title

No PR opened. Safe Markdown bootstrap committed directly to `main` because the repository was empty and the change was unambiguous.

## Commit message

`Initialize code handoff wiki and current repository policy`

Actual commits created during this repair:

1. `Initialize Jordan code handoff wiki`
2. `Add 2026-07-08 code handoff`

## Files to create/update

Created:

- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
- `docs/handoffs/2026-07-08-code-handoff.md`

## Files not to commit

Do not commit:

- raw FASTQ, BAM, SAM, CRAM, BAI, bigWig files
- archives or compressed data dumps
- SLURM logs, Euler output clutter, scratch folders, cache folders
- temporary renders or generated exploratory images
- duplicate scratch scripts such as `final.py`, `final_final.py`, `test.py`, `newplot.py`, `v2_fixed.py`, or `chatgpt_version.py`
- fake or simulated biological results unless explicitly marked as toy/simulated and kept separate from real analysis

## Scientific/data status

No clean canonical runnable analysis script was verified for commit in this run.

Current verified project constraints from available context:

- JM105 / Intronsaurus remains active.
- Figure 2 should be total/rRNA-depleted only unless Jordan explicitly reverses this.
- Poly-A data should not be used or shown for Figure 2 unless Jordan explicitly restores it.
- Experiments not yet done must be marked `NO DATA`.
- Do not fake biological data.
- Distinguish raw NMD-off/upf1D retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.

## Implementation notes

GitHub connector status at repair time:

- Repository resolved: `jorddyk/Jordan-McCarthy`
- Visibility: private
- Permissions: admin/push available
- Default branch: `main`
- Initial repository size: empty

Repair action:

- Bootstrapped the repository with Markdown-only governance and handoff documentation.
- No code was committed because no clean, verified canonical code was identified in the current run.
- This avoids preserving intermediate attempts while creating a stable place for future canonical code handoffs.

## Final code

No runnable code committed today.

The canonical output of this run is repository structure and policy:

```text
jorddyk/Jordan-McCarthy/
└── docs/
    ├── handoffs/
    │   └── 2026-07-08-code-handoff.md
    └── wiki/
        └── Jordan-McCarthy-Code-Wiki.md
```

## Code-focused self-counterintelligence

Detected risk: code and figure-rendering decisions are currently distributed across chats, Drive artifacts, scheduled-task prompts, and memory rather than a repo-centered source of truth.

Containment action taken: created `docs/wiki/Jordan-McCarthy-Code-Wiki.md` as the initial single source of truth for canonical code status, project constraints, and handoff rules.

Next containment action: when a clean canonical script is identified, commit it under a sensible project path instead of saving another chat-specific or scratch filename.
