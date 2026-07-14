# JM105 Figure 2 Euler rendering runbook and failure postmortem

Date created: 2026-07-14

Purpose: prevent future AI chats from repeating the failed Figure 2 rendering workflow and wasting Jordan's time.

## Canonical scope

- Final Figure 2 panels must be rendered reproducibly on Euler from the JM105 project tree.
- RNA panels use only total / rRNA-depleted JM105 data.
- Do not use poly-A, P-versus-T, mRNA-like, or P−T logic.
- Do not substitute locally generated ChatGPT images for publication figures.
- Source renderer currently located on Euler:
  - `/cluster/home/jmccarthy/JM105_Figure2_public_final_20260713_171245/scripts/render_jm105_figure2_public_final.py`
- Recovered mature panel renderers currently located under:
  - `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/`

## Required working style

1. Work directly on Euler when the raw data and renderers are already there.
2. Before running any recovered renderer, inspect its invocation contract. Do not guess arguments.
3. Run one renderer at a time until its exact CLI and outputs are verified.
4. Use direct `scp -r` for retrieval only after the Euler output directory is confirmed.
5. Do not introduce tar/ZIP/extraction unless there is a demonstrated need.
6. Do not print success after an error. Fail immediately and stop the command sequence.
7. Do not create a new wrapper until the existing renderer and its usage have been inspected.

## Confirmed Figure 2B invocation contract

The recovered hero-scatter renderer exits with:

```text
ERROR: Usage: figure2_panelA_v6_label_column.py <STRICT_ROOT> <OUTDIR>
```

Therefore this is wrong:

```bash
python3 figure2_panelA_v6_label_column.py
```

The renderer requires both positional arguments:

```bash
python3 figure2_panelA_v6_label_column.py "$STRICT_ROOT" "$OUTDIR"
```

Future chats must inspect the Figure 2D/E and Figure 2F renderers independently before invoking them. Their argument contracts must not be inferred from the Figure 2B contract.

## Failures on 2026-07-14

### 1. Repeated archive and extraction failures

What happened:
- PowerShell launchers created tar/ZIP layers and inferred nested local paths.
- Archive download was not verified before extraction.
- Variables were treated as proof that local files existed.
- Later commands continued after extraction failure and printed misleading completion text.

Avoid:
- `Compress-Archive` for deep recovered-source trees with long flattened filenames.
- tar creation followed by guessed nested extraction paths.
- citing or opening a local path unless `Test-Path` has passed.

Preferred:

```powershell
scp -r "jmccarthy@euler.ethz.ch:/confirmed/remote/out" "$env:USERPROFILE\Downloads\confirmed_local_name"
```

### 2. Downloaded PowerShell script blocked by ETH policy

What happened:
- A downloaded unsigned `.ps1` was invoked under enforced `RemoteSigned` policy.
- `Set-ExecutionPolicy -Scope Process Bypass` was overridden by a more specific policy.

Avoid:
- promising that process-scope policy changes will work on managed ETH systems.

If a downloaded script must be used:

```powershell
Unblock-File -LiteralPath $Script
& $Script
```

Better for this project: work directly on Euler when possible.

### 3. Legacy `bbox_inches="tight"` preflight stopped before rendering

What happened:
- A wrapper scanned recovered legacy scripts before patching them.
- It stopped on a known legacy fixed-canvas incompatibility rather than patching a run-specific copy.

Avoid:
- enforcing new renderer rules against unmodified historical scripts and treating that as a source failure.
- modifying the original historical renderer in place.

Preferred:
- copy to a run-specific executable file;
- patch only the save behavior;
- preserve the original;
- audit the executable copy.

### 4. Raw-text audit triggered on its own documentation

What happened:
- The audit searched for the literal `bbox_inches="tight"` anywhere in source text.
- It matched an explanatory comment saying that tight cropping was absent.

Avoid:
- regex auditing raw Python text for semantic code behavior.

Preferred:
- parse Python with `ast` and inspect only `savefig()` call keywords.

### 5. Patched renderer copied outside its source directory

Risk introduced:
- Legacy scripts may derive data and output paths from `__file__`.
- Moving a script into a generic patch directory can break relative-path assumptions.

Preferred:
- inspect path logic first;
- if `__file__`-relative, place a temporary patched copy inside the original renderer directory or pass explicit paths supported by the CLI.

### 6. Giant direct-Euler paste failed at the first recovered renderer

What happened:
- Jordan was already logged into Euler but was told to run `ssh jmccarthy@euler.ethz.ch` again, creating an unnecessary nested session.
- A very long pasted shell workflow was used before verifying each renderer's argument contract.
- Figure 2B failed with:

```text
ERROR: Usage: figure2_panelA_v6_label_column.py <STRICT_ROOT> <OUTDIR>
```

Root cause:
- the renderer was launched without its required positional arguments.

Avoid:
- nested SSH when the prompt already shows `jmccarthy@eu-login-*`.
- large all-panel commands before the first renderer has run successfully.
- guessing invocation signatures.

Preferred diagnostic before execution:

```bash
python3 /path/to/renderer.py --help 2>&1 || true
grep -nE 'Usage:|sys\.argv|argparse|ArgumentParser' /path/to/renderer.py | head -80
```

Then run only that renderer with its actual arguments.

## Minimal safe Euler sequence

When already on Euler:

```bash
set -euo pipefail

PROJECT_ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq"
STRICT_ROOT="$PROJECT_ROOT/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE"
B_DIR="$STRICT_ROOT/PanelA_reset_render_v6_LABEL_COLUMN_FINAL"
B_SCRIPT="$B_DIR/figure2_panelA_v6_label_column.py"
OUTDIR="/cluster/home/jmccarthy/JM105_Figure2_work/panel_B"

mkdir -p "$OUTDIR"

module load fast_python_workshop_cpu/2025.0.0
command -v venv_cpu_init >/dev/null 2>&1 && venv_cpu_init

python3 "$B_SCRIPT" "$STRICT_ROOT" "$OUTDIR"
find "$OUTDIR" -maxdepth 2 -type f -printf '%P\t%s bytes\n' | sort
```

Do not proceed to D/E or F until B outputs are confirmed.

## Current source-correctness warning

The public-final composite renderer previously selected a 402-row strict annotated universe but recomputed candidates from effect thresholds alone. It ignored explicit gate columns and admitted mitochondrial transcripts. Future rendering must use explicit strict gate columns and must not infer final candidates only from `aging_effect > 0.15` and `CR_suppression > 0.15`.

## Publication render contract

- fixed declared canvas;
- transparent SVG, PDF, PNG;
- separate white-background preview PNG;
- editable SVG text (`svg.fonttype = none`);
- Arial-compatible font request;
- no automatic tight cropping;
- lane map before code;
- exact collision inventory before patching;
- final lane-by-lane audit;
- all plotted values exported with provenance.

## Canonical destination once accepted

Accepted exact source should be committed under:

```text
projects/figure-rendering/panel-renderers/jm105-figure2-public-final/
```

Do not commit failed wrappers as canonical renderers. Keep failure lessons in this runbook and commit only an accepted renderer plus its minimal Euler runner and retrieval instructions.
