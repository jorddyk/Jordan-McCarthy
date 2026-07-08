# Legacy Code Backfill GitHub Import Prompt

Purpose: canonical one-time / periodic prompt for recovering old useful code from ChatGPT/project history and committing it to the private GitHub repository.

Original source clue/conversation context: user-provided prompt in JM105 RNA Seq Analysis project conversation on 2026-07-08.

Expected inputs: accessible old ChatGPT/project history, uploaded files, File Library results, Google Drive artifacts, code blocks, scripts, macros, PowerShell commands, Euler/sbatch jobs, R/Python/Bash/Fiji/Groovy/HTML code, and GitHub access.

Expected outputs: recovered canonical code under human-purpose project paths, updated README/backfill/wiki docs, concise CODE HANDOFF, and email to `jordymac18@gmail.com` with subject `Daily code handoff`.

Known assumptions: repo is `jorddyk/Jordan-McCarthy`; code should be organized by project/purpose, not daily handoff; do not invent missing code; do not commit raw data or generated clutter.

Data status: prompt/workflow artifact only. It contains no biological data and is not runnable code.

---

You are performing a LEGACY CODE BACKFILL into my private GitHub repo `jorddyk/Jordan-McCarthy`.

This is not a daily handoff summary. Your job is to search deeply through this project’s old ChatGPT conversations, uploaded files, File Library results, Google Drive artifacts, code blocks, scripts, macros, PowerShell commands, Euler/sbatch jobs, R/Python/Bash/Fiji/Groovy/HTML code, and any other Jordan-authorized sources available in this project, then recover the most complete, most recent, most useful canonical code and save it into GitHub.

Repository rule:
Organize code by project and what it actually does, not by date or handoff. Daily handoff files are audit logs only.

Canonical repo:
`jorddyk/Jordan-McCarthy`

Use these project folders:

- JM105 / Intronsaurus code:
  `projects/jm105-intronsaurus/`

- Figure rendering / Nature Aging mockups:
  `projects/figure-rendering/`

- ImageJ / Fiji / aging-chip macros:
  `projects/imagej-fiji-aging-chips/`

- German/TELC/language-learning apps:
  `projects/language-learning/`

- Personal intelligence agency prompts/rubrics:
  `projects/personal-intelligence-agency/`

Your workflow:

1. Search far back in this project’s conversation history.
   Do not only look at today’s chat. Search old messages for exact code blocks, filenames, output folders, job IDs, script names, snippets, and project-specific phrases.

2. Identify candidate code.
   Prioritize complete runnable scripts/macros/apps over summaries. Look for Python, R, Bash, PowerShell, sbatch, Fiji `.ijm`, Groovy, HTML/CSS/JS, and notebook/script code.

3. Decide what is canonical.
   Keep the newest useful version, not every intermediate attempt. Do not save duplicate scratch versions like `final.py`, `test.py`, `newplot.py`, `v2_fixed.py`, `chatgpt_version.py`, or date-only names unless only as deprecated archive with a clear reason.

4. Save under human file names.
   Use names that describe what the code does.

   Examples:
   - `projects/jm105-intronsaurus/analysis/jm101-jm105-integrate-intronsaurus.py`
   - `projects/jm105-intronsaurus/alignment/jm101-star-align-array.sbatch`
   - `projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py`
   - `projects/figure-rendering/panel-renderers/render-no-data-placeholder.py`
   - `projects/imagej-fiji-aging-chips/macros/jm128-split-nd2-positions-bioformats.ijm`
   - `projects/imagej-fiji-aging-chips/groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`
   - `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`

5. Do not invent missing code.
   If you only find a summary, memory, or truncated snippet, do not reconstruct it and pretend it is recovered. Instead update the relevant `docs/legacy-code-backfill.md` file with:
   - historical filename/source clue
   - what the code was supposed to do
   - likely canonical path
   - status: `exact full source not yet recovered`

6. For recovered code, add a short header comment.
   Include:
   - human purpose
   - original source clue/conversation context
   - expected inputs
   - expected outputs
   - known assumptions
   - whether it uses real data, toy/simulated data, or `NO DATA` placeholders

7. Protect scientific integrity.
   Never generate fake biological data.
   If an experiment or panel has not been performed, mark it `NO DATA`.
   For JM105/Intronsaurus, preserve these constraints:
   - Figure 2 is total/rRNA-depleted only unless Jordan explicitly reverses this.
   - Do not use poly-A data in Figure 2 unless explicitly restored.
   - Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
   - Distinguish RNA/host transcript abundance from protein abundance.
   - Do not claim caloric restriction is starvation.

8. Protect microscopy quantification.
   For ImageJ/Fiji/MitoSOX workflows:
   - do not commit raw ND2 or TIFF stacks
   - do not silently convert quantitative data to 8-bit
   - do not silently apply auto-contrast to quantitative data
   - document channel, Z, T, frame-sampling, background-subtraction, and output naming
   - preserve exact aging-chip paths/output conventions when they are part of the macro

9. GitHub execution:
   First verify `jorddyk/Jordan-McCarthy` exists, is private, and is writable.
   Fetch existing project README/backfill files before writing.
   If a file exists, update it using its SHA.
   If a file does not exist, create it.
   Commit directly to `main` for safe Markdown or small clearly canonical scripts.
   Use a branch/PR if the change is large, ambiguous, or modifies many runnable files.

10. Update documentation.
   After saving code, update the relevant project README and/or legacy backfill file.
   Also update `docs/wiki/Jordan-McCarthy-Code-Wiki.md` with canonical paths and status.

11. Produce a concise final CODE HANDOFF with:
   - Repo
   - Project area
   - Human purpose
   - Files created/updated
   - Files deliberately not committed
   - Scientific/data status
   - Implementation notes
   - Final code paths
   - Legacy-backfill progress
   - Any remaining source-recovery targets

12. Send Jordan an email at `jordymac18@gmail.com` with subject `Daily code handoff`.
   The email should say what project files changed, whether actual code was imported, what remains pending, and any important caution.

Important:
This is a one-time beginning-of-repo backfill. Be patient and search deeply. The goal is to rescue old useful code from ChatGPT/project history into GitHub so future scheduled handoffs only need to maintain it incrementally.
