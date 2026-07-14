# JM105 Figure 2 PowerShell variable-colon guardrail

Date: 2026-07-14

## Failure

The Figure 2 v3.1 PowerShell runner failed to parse before execution because two interpolated error messages contained a bare variable immediately followed by a colon:

```powershell
"Malformed Panel 2A row $Row: ..."
"Unexpected Panel 2A glucose value at worksheet row $Row: $Glucose"
```

PowerShell interprets `$Row:` as a scoped or drive-qualified variable reference. Because `Row` is not a valid scope/drive prefix in that form, the script fails at parse time.

## Required syntax

Use braces whenever punctuation immediately follows an interpolated variable:

```powershell
"Malformed Panel 2A row ${Row}: ..."
"Unexpected Panel 2A glucose value at worksheet row ${Row}: $Glucose"
```

## Permanent preflight rule

Before delivering any PowerShell figure runner:

1. Scan the complete `.ps1` for bare `$Variable:` patterns.
2. Allow only genuine scope prefixes such as `$env:`, `$global:`, `$script:`, `$local:`, `$private:`, and `$using:`.
3. Convert all ordinary variable-plus-colon interpolations to `${Variable}:`.
4. Run a PowerShell parser check when PowerShell is available.
5. When PowerShell is unavailable in the build environment, run the static interpolation-hazard audit and state that exact limitation.
6. Do not make the user discover parse errors after downloading and extracting a package.

## Figure 2 v3.2 correction

The corrected runner changes only the two parser-hazard strings. Figure geometry, biological data, source selection, lane assignments, and output contract are unchanged.

The corrected package must still validate Panel 2A as exactly 150 biological records: 52 cells at 2% glucose and 98 cells at 0.5% glucose CR. Excel `UsedRange` remains a scan boundary only.
