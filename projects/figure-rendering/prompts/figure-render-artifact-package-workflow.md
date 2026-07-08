# Figure Render Artifact Package Workflow

Purpose: reusable prompt/spec artifact for making downloadable figure-rendering code packages that Jordan can run from Windows PowerShell on Euler.

Original source clue/conversation context: recovered from the July 2026 conversation after comparing an artifact-package response with prior one-script/PowerShell workflows. The key correction was that the preferred deliverable is one ZIP package plus one PowerShell runner, with strict data-integrity mode by default.

Expected inputs: figure-specific `.docx` source-of-truth document, visual mockup/PPT/screenshot, real data paths, and target figure number.

Expected outputs when used: one downloadable ZIP containing complete render source and helper scripts, plus a downloadable PowerShell runner or short one-command run instruction.

Known assumptions: prompt/spec artifact only; not runnable code. It defines how future figure-rendering chats should package code.

Data status: no real data used here; no toy/simulated data generated; no `NO DATA` placeholders rendered.

---

## Preferred deliverable format

The artifact workflow should be simple and robust.

Do not make Jordan manually copy long code blocks. Do not make Jordan manually coordinate many separate files unless they are also included in one ZIP.

Preferred deliverable:

```text
Figure<N>_render_artifact_package.zip
```

The ZIP must contain:

```text
render_figure<N>_all_panels.py
run_figure<N>_on_euler.sh
retrieve_figure<N>_outputs.ps1
README_Figure<N>_run_instructions.txt
any helper config files needed by the renderer
```

Also provide `retrieve_figure<N>_outputs.ps1` as a separate downloadable file when useful, or paste only the short command needed to run it.

## PowerShell workflow

Jordan should be able to:

1. Download the ZIP on Windows.
2. Open PowerShell in the download folder.
3. Run one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\retrieve_figure<N>_outputs.ps1
```

The PowerShell script must:

- find `Figure<N>_render_artifact_package.zip` in the current folder
- upload the ZIP to Euler
- unzip it into the correct remote run directory
- run syntax preflight on the Python script
- run or submit the Euler render job
- wait for completion if practical, or print exact monitoring commands
- retrieve SVG/PDF/PNG/previews/audits/logs into the Windows output folder
- print the exact local output folder at the end

## User-facing response format

The response should include:

1. ZIP download link first.
2. PowerShell runner download link second.
3. One PowerShell command to run.
4. Very short note about where outputs will be retrieved.

Ideal response shape:

```text
Done.

Main package:
[Figure<N>_render_artifact_package.zip](sandbox:/mnt/data/Figure<N>_render_artifact_package.zip)

PowerShell runner:
[retrieve_figure<N>_outputs.ps1](sandbox:/mnt/data/retrieve_figure<N>_outputs.ps1)

Run from PowerShell in the download folder:

powershell -ExecutionPolicy Bypass -File .\retrieve_figure<N>_outputs.ps1

Outputs will be retrieved to:
Y:\Jordan\JM105_RNAseq\Figure<N>_render_download
```

## Strict data-integrity mode

Strict data-integrity mode is required by default.

Do not "generate what can be generated" if required figure data are missing. Missing required files, columns, conditions, genotypes, replicates, formulas, or provenance must hard-stop the final render unless Jordan explicitly requests draft mode.

If blocked, write:

```text
missing_requirements.tsv
```

and stop.

Do not:

- create placeholder plots that look like real data
- use mockup numbers as data
- silently omit panels
- silently render partial panels

Allowed behavior:

- If all required data and provenance exist for all required panels, render all panels.
- If any required data for any required panel are missing, stop before final rendering unless Jordan explicitly requests partial draft mode.
- In draft mode, every affected output must be visibly and programmatically marked `DRAFT`, `PARTIAL`, or `NOT FOR PUBLICATION`.

## Required renderer behavior

The Python script must:

- parse the uploaded figure docx as the biological/data source of truth
- inspect the uploaded figure mockup as the visual source of truth
- produce a panel contract table before rendering
- enforce aspect ratios per panel
- render no internal figure letters and no internal big figure titles
- produce transparent SVG/PDF/PNG plus white preview PNG
- preserve SVG text as editable text
- avoid `bbox_inches="tight"`
- write provenance, input manifest, data integrity audit, layout decisions, text layout audit, text overlap audit, output manifest, and `missing_requirements.tsv` if blocked
- hard-stop if required data/provenance are missing

The PowerShell script must:

- upload the renderer/package to Euler
- run syntax preflight
- run or submit the Euler job
- retrieve SVG/PDF/PNG/previews/audits/logs
- print the exact local output folder

The README must include:

- run order
- expected outputs
- exact Euler paths
- exact Windows retrieval folder
- what to inspect after rendering
- what PASS/FAIL flags mean
