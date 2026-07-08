# Code Handoff

## Recovery metadata

- Human purpose: Daily code-handoff and legacy-backfill automation prompt for preserving clean canonical code in Jordan's private GitHub repository `jorddyk/Jordan-McCarthy`.
- Original source clue/conversation context: Recovered exactly from active ChatGPT scheduled task `Code Handoff` during the 2026-07-08 legacy code backfill.
- Expected inputs: GitHub repository metadata and files; old ChatGPT/project context; File Library/file-search results; Google Drive; Gmail attachments where relevant; Jordan-authorized sources.
- Expected outputs: Canonical project-organized code commits or source-recovery documentation, updated README/wiki/handoff files, and a `Daily code handoff` email to Jordan.
- Known assumptions: Repo organization is by project and purpose, not by date. Daily handoffs are audit logs only. The prompt includes strict scientific/data and microscopy integrity rules.
- Data status: Prompt/spec artifact only. No biological data, no raw code dump, no generated analysis output.

## Schedule metadata at recovery

```text
Title: Code Handoff
Timing mode: flexible_schedule
Schedule:
BEGIN:VEVENT
DTSTART:20260707T104904
RRULE:FREQ=DAILY
END:VEVENT
Notifications enabled: false
Email enabled: false
```

## Exact recovered prompt

```text
Prepare and maintain Jordan's daily CODE HANDOFF for the private GitHub repository `jorddyk/Jordan-McCarthy`. Treat this repo as the canonical private code vault unless Jordan explicitly changes it.

Primary goal: preserve clean, useful, most-current canonical code in a human-organized repository. The repository must be organized by PROJECT and CODE PURPOSE, not by daily handoff date. Daily handoffs are audit logs only.

Important current bootstrapping context: the repo is still in its initial legacy-backfill phase. Do not only scan today's chat. Each run should recover a small batch of historical code from older ChatGPT/project context and authorized sources until the major legacy code areas are represented in GitHub. Prioritize exact complete code recovery over speed.

Mandatory repository organization:

- Put JM105 / Intronsaurus RNA-seq, intron retention, leakage, NMD, Mud1/CR, figure, and manuscript-support code under `projects/jm105-intronsaurus/`.
- Put reusable figure-rendering, panel-rendering, and Nature Aging-style mockup code under `projects/figure-rendering/`.
- Put ImageJ/Fiji/Groovy aging-chip, MitoSOX, ROS, BF/FL, ND2 splitting/stitching, microfluidic aging-chip processing, and quantitative microscopy macros under `projects/imagej-fiji-aging-chips/`.
- Put German/TELC/language-learning web apps and study tools under `projects/language-learning/`.
- Put scheduled-task prompts, scoring rubrics, and personal intelligence automation support under `projects/personal-intelligence-agency/`.
- Keep `docs/handoffs/YYYY-MM-DD-code-handoff.md` as an audit trail only. Do not use daily handoff folders as the primary code structure.
- Maintain the human-facing repo index at `README.md`, `projects/README.md`, and project-specific README files.

Mandatory execution order:

1. Verify GitHub access first.
   - Use GitHub repository metadata for `jorddyk/Jordan-McCarthy`.
   - Confirm the repo exists, is private, and is writable.
   - Use the default branch unless there is a clear reason to create a branch.

2. Inspect the project-first structure before writing.
   - Fetch `README.md`, `projects/README.md`, and `docs/wiki/Jordan-McCarthy-Code-Wiki.md`.
   - Fetch or create/update the relevant project README before adding code.
   - Fetch today's handoff path `docs/handoffs/YYYY-MM-DD-code-handoff.md` only after deciding what project files changed.

3. Legacy-backfill search, not just daily scanning.
   - Search old ChatGPT/project context and accessible memory for exact code-bearing conversations, not merely summaries.
   - Search File Library/file-search results, Google Drive, GitHub state, Gmail attachments if relevant, and other Jordan-authorized sources.
   - Use exact historical filenames, path fragments, output names, job IDs, and code strings as search keys.
   - Mclick/open promising file-library results when snippets are incomplete.
   - When exact complete code cannot be retrieved, create/update a `docs/legacy-code-backfill.md` file inside the relevant project with source clues, proposed human filename, and status `exact full source not yet recovered`; do not pretend a summary is source code.

4. Current legacy priority queues.
   - JM105/Intronsaurus: recover `110_JM101_JM105_integrate_intronsaurus.py`, `111_JM101_STAR_align_array.sbatch`, `112_JM101_integrate_after_STAR.sbatch`, upload/submit PowerShell helpers, Rsubread Step 2 hard-resume/turbo scripts, Step 3 DESeq2, IRFinder drafts, Intronsaurus interactive reader bundles such as vNext3 and vNext3AE.
   - Figure rendering: recover Nature Aging/Yves-compatible figure mockup renderers, scoring-model code, Figure 5 renderer, NO DATA placeholder renderer, JM133/JM134 label audit/rerender utilities.
   - ImageJ/Fiji aging chips: recover JM128/JM129 macros and Groovy scripts, especially Bio-Formats ND2 splitting, position hyperstack export, MitoSOX C2 extraction, BF/FL merge macros, ROS/RLS aging-chip processing, virtual hyperstack construction, and quantitative MitoSOX background-subtraction workflows. Highest-priority known source clues include `Image001.nd2`, `Image001_Pos0_Hyperstack.tif`, `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions`, `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`, `rollingBallRadius=100`, `C=2`, `Z=60`, `T=107/139/145`, and output names like `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif` and `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif`.
   - Language-learning: recover full single-file HTML apps only when complete source is available from `<!DOCTYPE html>` through `</html>`.

5. Extract only complete, clean, most-current canonical code.
   - Prefer updating existing canonical files over creating new files.
   - Do not commit truncated code, partial snippets, or incomplete files.
   - A web app is canonical only when the complete file from `<!DOCTYPE html>` through `</html>` is available.
   - A Fiji macro/Groovy/Python/R/Bash/PowerShell script is canonical only when complete enough to run or intentionally documented as a template.
   - If exact recovered code is obsolete but historically useful, save it under `archive/` inside the project and mark it deprecated in the README. Prefer latest canonical version for active project files.
   - If no clean canonical runnable code is verified, do not invent code. Update only project README/wiki/handoff/backfill metadata if useful.

6. Use human file names.
   - Good: `projects/imagej-fiji-aging-chips/macros/jm128-split-nd2-positions-bioformats.ijm`.
   - Good: `projects/imagej-fiji-aging-chips/groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`.
   - Good: `projects/jm105-intronsaurus/analysis/jm101-jm105-integrate-intronsaurus.py`.
   - Good: `projects/jm105-intronsaurus/alignment/jm101-star-align-array.sbatch`.
   - Good: `projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py`.
   - Good: `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`.
   - Bad: `final.py`, `test.py`, `newplot.py`, `german-drill-6.html`, `WORKING.html`, `chatgpt_version.py`, date-only names.

Every run must produce or update a CODE HANDOFF with this exact structure:
- Repo
- Project area
- Human purpose
- Branch name
- PR title
- Commit message
- Project files created/updated
- Handoff/audit files created/updated
- Files not to commit
- Scientific/data status
- Implementation notes
- Final code or candidate imports
- Legacy-backfill progress

Also maintain the self-updating Jordan McCarthy code wiki at `docs/wiki/Jordan-McCarthy-Code-Wiki.md`. The wiki should summarize canonical scripts, repo paths, supported figures/panels/claims, required inputs, outputs, runtime environment, data status, candidate imports, legacy-backfill queue status, and last-known canonical decisions. Update the wiki only from verified handoff content and accessible project/chat context. Do not add speculative scripts or unsupported claims.

Hard rules:
- Never generate fake biological data.
- If an experiment has not been done, outputs must clearly say `NO DATA`.
- Distinguish real data, simulated toy data, and `NO DATA` placeholders.
- Do not commit raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, ND2, TIFF stacks, archives, logs, scratch folders, temporary plots, Euler output clutter, cache folders, or duplicate scripts.
- Do not commit private raw image data or large generated microscopy outputs.
- Exclude private clutter, generated temporary renders, SLURM logs, cache folders, and accidental binary/archive outputs unless Jordan explicitly asks otherwise.
- For quantitative MitoSOX/ImageJ workflows, do not silently add 8-bit conversion or auto-contrast. Background subtraction and display-only contrast must be explicit and documented.

Code-focused self-counterintelligence layer:
Detect whether Jordan's code ecosystem is creating internal risk through script sprawl, repeated one-off fixes, inconsistent data labels, uncommitted canonical code, hidden dependency assumptions, prompt churn, figure mockups that violate original panel/aspect-ratio constraints, confusing simulated/real/NO DATA status, daily-handoff logs replacing project organization, or legacy code remaining trapped in old chats. This layer should protect execution and reproducibility; it should not become a psychological review. If a risk is found, include one containment action such as canonicalize one script, update the relevant project README/backfill queue, name a single source of truth, mark a panel as NO DATA, or move logic from handoff-oriented thinking into project-oriented structure.

Failure-handling rules:
- If GitHub create-file fails because the file already exists, fetch the file and update it using its SHA.
- If GitHub update-file fails because the SHA is stale, refetch the file and retry once.
- If GitHub writes are not available, return a complete handoff in the task output and state exactly which connector/write step failed.
- Do not claim GitHub permissions are blocked unless the connector action explicitly failed.
- Always distinguish: no canonical code found vs incomplete/truncated source vs connector failure vs email-delivery failure.
- If a source search only returns a summary of prior code, record it as a recovery clue, not recovered code.

For each proposed code commit, use sensible project paths and human filenames. For Markdown-only project README/wiki/handoff/backfill maintenance, direct commits to `main` are acceptable when safe. Create a branch/PR for runnable code changes when the change is substantial or ambiguous.

Send Jordan an email at jordymac18@gmail.com after each run with subject "Daily code handoff". The email should summarize project files changed first, handoff/backfill files second, whether actual canonical code was imported, which candidate imports remain pending, any branch/PR/commit information, and any code-focused internal execution risk plus containment action. Do not include huge code blocks in the email unless essential; point to repo paths or task output for full code.
```
