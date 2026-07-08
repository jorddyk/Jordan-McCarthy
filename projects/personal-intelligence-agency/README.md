# Personal Intelligence Agency

Human goal: preserve prompts, scoring rubrics, automation specs, and support code for Jordan's private strategic-intelligence system.

This project is for system design and automation logic, not private raw inbox/calendar dumps.

## Intended structure

```text
projects/personal-intelligence-agency/
  prompts/
    Canonical scheduled-task prompts.
  rubrics/
    Signal scoring models and action thresholds.
  reports/
    Reusable report templates, not daily output spam.
```

## Current automation desks

- Strategic Alert Triage
- Science Preemption Watch
- Swiss Leverage Radar
- Strategic Brief Redteam
- Code Handoff

## Canonical prompt/spec artifacts

| Path | Purpose | Status |
|---|---|---|
| `prompts/legacy-code-backfill-github-import.md` | Exact prompt for recovering useful code from old project conversations and committing canonical source to `jorddyk/Jordan-McCarthy`. | Imported in legacy backfill. |

## Canonicality rule

Save the reusable system logic here. Do not save every daily alert unless it changes the model, scoring rubric, or task design.
