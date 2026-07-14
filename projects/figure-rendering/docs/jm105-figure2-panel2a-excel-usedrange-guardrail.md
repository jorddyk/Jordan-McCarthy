# JM105 Figure 2A Excel export guardrail

Date: 2026-07-14

## Failure recorded

The Figure 2 v3 PowerShell runner opened:

`Y:\for Yves\Jordan\Spliceosome Shift CR Paper\Figure 2\Panel2A_Jm104_AnalysisJordan.xlsx`

and used `Worksheet.UsedRange.Rows.Count` as though it were the biological data-row count. Excel's UsedRange extended two rows beyond the 150 biological records because formatted blank rows remained in the sheet. The runner exported those rows and then failed with:

`Panel A TSV has 152 data rows; expected 150.`

The workbook itself contains 150 biological records:

- 2% glucose control: n=52
- 0.5% glucose CR: n=98

## Permanent rule

`UsedRange` is a scan boundary only. It is never proof of biological row count.

For this workbook and future Excel-sourced figure panels:

1. Iterate through the UsedRange only as an upper bound.
2. Define explicit core biological fields for row identity.
3. Skip a row only when all core fields are blank.
4. Fail on partially populated core rows instead of silently dropping them.
5. Preserve optional blank fields such as censor/event metadata or frame-at-death where allowed.
6. Validate parsed biological records, not physical TSV text lines.
7. For Panel 2A, require exactly 150 parsed records, with 52 at 2% glucose and 98 at 0.5% glucose CR.
8. Use `Import-Csv -Delimiter "`t"` or another actual table parser for post-export validation. Do not use `Get-Content.Count` as a row-count validator because quoted multiline headers or fields can change physical line counts.
9. Move the runner working directory away from `C:\WINDOWS\system32` before generating local files.
10. Do not launch Euler until the source-export validation passes.

## Correct filtering key for Panel 2A

The core fields are:

- Position
- Genotype
- % Glucose
- RLS

`Image Path` may be blank. `Event` and `Frame at death` may be blank where biologically appropriate. A row with all four core fields blank is an empty formatted row and must not be exported.

## Acceptance check before rendering

The runner must print:

`Panel A source validated: n=150; 2% glucose n=52; 0.5% glucose CR n=98.`

Only after this message may it upload inputs and render Figure 2 A-F on Euler.
