# Legacy Code Backfill to GitHub

Human purpose: one-time beginning-of-repo recovery prompt for searching old ChatGPT/project history and importing canonical code into Jordan's private GitHub repo.

Original source clue / conversation context: Jordan explicitly requested a legacy code backfill into `jorddyk/Jordan-McCarthy`, organized by project and function rather than date/handoff.

Expected inputs: old ChatGPT project conversations, uploaded files, File Library results, Google Drive artifacts, code blocks, scripts, macros, PowerShell commands, Euler/sbatch jobs, R/Python/Bash/Fiji/Groovy/HTML code, and other Jordan-authorized sources.

Expected outputs: canonical project-path code files, updated READMEs/backfill docs/wiki, concise final code handoff, and a handoff email to `jordymac18@gmail.com`.

Known assumptions: this is a recovery/import prompt, not an analysis script. It does not generate biological data.

Data status: prompt/rubric only.

---

## Prompt

You are performing a LEGACY CODE BACKFILL into my private GitHub repo `jorddyk/Jordan-McCarthy`.

This is not a daily handoff summary. Your job is to search deeply through this project’s old ChatGPT conversations, uploaded files, File Library results, Google Drive artifacts, code blocks, scripts, macros, PowerShell commands, Euler/sbatch jobs, R/Python/Bash/Fiji/Groovy/HTML code, and any other Jordan-authorized sources available in this project, then recover the most complete, most recent, most useful canonical code and save it into GitHub.

Repository rule:
Organize code by project and what it actually does, not by date or handoff. Daily handoff files are audit logs only.

Canonical repo:
`jorddyk/Jordan-McCarthy`

Use these project folders:

- JM105 / Intronsaurus code: `projects/jm105-intronsaurus/`
- Figure rendering / Nature Aging mockups: `projects/figure-rendering/`
- ImageJ / Fiji / aging-chip macros: `projects/imagej-fiji-aging-chips/`
- German/TELC/language-learning apps: `projects/language-learning/`
- Personal intelligence agency prompts/rubrics: `projects/personal-intelligence-agency/`

Workflow:

1. Search far back in this project’s conversation history. Do not only look at today’s chat. Search old messages for exact code blocks, filenames, output folders, job IDs, script names, snippets, and project-specific phrases.
2. Identify candidate code. Prioritize complete runnable scripts/macros/apps over summaries.
3. Decide what is canonical. Keep the newest useful version, not every intermediate attempt.
4. Save under human file names.
5. Do not invent missing code. If only a summary is found, update the relevant `docs/legacy-code-backfill.md` file with source clues and status `exact full source not yet recovered`.
6. For recovered code, add a short header comment with purpose, source clue, expected inputs/outputs, known assumptions, and data status.
7. Protect scientific integrity. Never generate fake biological data; mark missing panels `NO DATA`; for JM105 Figure 2, use total/rRNA-depleted data only unless Jordan explicitly reverses this; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal; distinguish RNA/host transcript abundance from protein abundance; do not claim caloric restriction is starvation.
8. Protect microscopy quantification. Do not commit raw ND2/TIFF stacks; do not silently convert quantitative data to 8-bit; do not silently apply auto-contrast to quantitative data; document channel, Z, T, frame-sampling, background subtraction, and output naming.
9. Verify `jorddyk/Jordan-McCarthy` exists, is private, and writable before writing.
10. Update project READMEs/backfill docs and `docs/wiki/Jordan-McCarthy-Code-Wiki.md`.
11. Produce a concise final CODE HANDOFF with repo, project area, purpose, files changed, files not committed, data status, implementation notes, final code paths, progress, and remaining recovery targets.
12. Send Jordan an email at `jordymac18@gmail.com` with subject `Daily code handoff`.
