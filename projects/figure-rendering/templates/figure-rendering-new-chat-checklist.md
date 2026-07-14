# Mandatory new-chat checklist for manuscript figure rendering

Before responding with code or a render, read:

1. `projects/figure-rendering/START_HERE_FOR_FIGURE_RENDERING.md`
2. `projects/figure-rendering/AGENTS.md`
3. `projects/figure-rendering/docs/figure-rendering-reliability-standard.md`
4. `projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md`
5. the relevant figure/panel source lock and accepted renderer README;
6. the Google Drive Figure Acceptance Matrix, Definitions Lock, Decision Rules, and Action Log.

Then complete this checklist:

```text
REQUEST SCOPE
figure:
requested panels:
full figure or staged subset:

PANEL IDENTITY
current composite/deck:
slide/page:
identity of each panel:
accepted visual reference:
forbidden substitutions:

SOURCE LOCK
source path(s):
raw or enriched:
sheet/table:
required columns:
biological unit per row:
expected row/group counts:
name-resolution fields:
renderer CLI:

ENVIRONMENT PREFLIGHT
PowerShell parser: PASS/FAIL
Bash syntax: PASS/FAIL
Python compile: PASS/FAIL
Euler module/environment:
resolved target font:

LAYOUT
lane map emitted:
collision inventory emitted:
fixed canvas dimensions:

TARGET-ENVIRONMENT QA
all requested panels rendered on Euler:
clipped text count per panel:
text-overlap count per panel:
legend-data intersections:
point-label intersections:
visible systematic identifiers:
required artifact existence:

DELIVERY
remote output path:
PowerShell retrieval included in same response:
local output verification:
white preview opened:
Drive Action Log updated:
GitHub canonical code/docs updated:
```

Do not proceed past a failed line. Do not substitute a local preflight for the Euler render. Do not report completion until the retrieval and local verification lines pass.