# Figure-rendering workflow for AI agents

Before creating or editing figure code in this directory, read:

- `START_HERE_FOR_FIGURE_RENDERING.md`
- `docs/figure-rendering-reliability-standard.md`
- `templates/jm105-figure-rendering-learning-loop.md`
- the relevant panel source lock and accepted renderer README

Required workflow:

1. Preserve the panel identity and aspect ratio defined by the current authoritative composite.
2. Treat a complete-figure request as every panel unless the user explicitly authorizes a subset.
3. Verify source paths, table schemas, row and group counts, gene aliases, real metadata spellings, and renderer arguments before rendering.
4. Check PowerShell syntax, Bash syntax, Python compilation, parser regression cases, and exact-table metadata normalization before delivery or Slurm submission.
5. Execute the renderer in the target Euler environment and record the resolved font.
6. Test the target font and an expected fallback font with the post-draw collision audit.
7. Stop the run when clipping, text overlap, legend-data contact, point-label contact, missing objects, literal NaN cells, visible systematic identifiers, or missing artifacts are detected.
8. Use fixed canvases, preserve editable SVG text, and avoid automatic tight cropping.
9. Include the Windows retrieval and local verification step with the render delivery.
10. Update the Google Drive Action Log after material failures, corrections, renders, acceptance decisions, and GitHub updates.
11. Keep only the Jordan-accepted canonical renderer in the repository; describe failed intermediate attempts in one incident record rather than storing many near-duplicate scripts.
12. Convert every material failure into a regression test or machine-checkable guard before the next submission.
