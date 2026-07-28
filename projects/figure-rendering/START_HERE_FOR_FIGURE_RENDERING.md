# START HERE FOR FIGURE RENDERING

This is the first file every new AI chat must read before rendering a manuscript figure in this repository.

## Mandatory files

1. `AGENTS.md`
2. `docs/figure-rendering-reliability-standard.md`
3. `templates/jm105-figure-rendering-learning-loop.md`
4. `templates/figure-rendering-new-chat-checklist.md`
5. `templates/nature-aging-figure-rendering-new-chat-prompt-v2.md`
6. `templates/chatgpt-jm105-rendering-operating-standard.md`
7. the relevant accepted renderer README and panel/source lock;
8. the Google Drive `JM105 Intronsaurus Figure Acceptance Matrix` tabs: Acceptance Matrix, Definitions Lock, Decision Rules, Action Log.

For the next pipeline figure, Figure 3, also read:

```text
prompts/jm105-figure3-new-chat-starting-prompt.md
docs/jm105-figure3-current-panel-crosswalk-and-design-brief.md
docs/jm105-figure3-2026-07-28-rendering-incident-and-learning-record.md
```

## Non-negotiable summary

- Lock panel identity from the current PowerPoint/composite before code.
- A full-figure request means all panels.
- Do not change panel type because another source or renderer is easier.
- Verify paths, CLI, schema, row counts, group counts, aliases and real metadata spellings before rendering.
- Run `qa/jm105_metadata_preflight.py` or an equivalent exact-table preflight before Slurm submission.
- Render in the actual Euler environment and record the resolved font.
- Run the hard post-draw collision gate on the final target-environment render.
- No text overlap, clipping, legend-data overlap, point-label overlap, literal NaN cells or visible systematic IDs.
- Fixed canvas; no automatic tight crop; editable SVG text.
- Every response that renders must also provide exact retrieval code and verified downloadable outputs.
- Record failures and proven fixes in GitHub and the Drive Action Log.
- Commit only the Jordan-accepted canonical renderer, not failed intermediate versions.

The complete 2026-07-14 failure/recovery record is in `docs/jm105-figure2-2026-07-14-complete-incident-postmortem.md`. The successful implementation reference is `panel-renderers/jm105-figure2-v4_1/`.
