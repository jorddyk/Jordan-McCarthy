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
| `prompts/code-handoff.md` | Exact active scheduled-task prompt for daily project-organized code handoff and continuing legacy source recovery. | Imported from active automation on 2026-07-08. |
| `prompts/strategic-alert-triage.md` | Exact active scheduled-task prompt for daily urgent strategic signal triage with action thresholds and bounded self-counterintelligence. | Imported from active automation on 2026-07-08. |
| `prompts/science-preemption-watch.md` | Exact active scheduled-task prompt for monitoring scientific preemption, claim-framing risk, and JM105/Intronsaurus novelty. | Imported from active automation on 2026-07-08. |
| `prompts/swiss-leverage-radar.md` | Exact active scheduled-task prompt for Swiss/ETH funding, startup, career, IP, and leverage signals. | Imported from active automation on 2026-07-08. |
| `prompts/weekly-strategic-brief-redteam.md` | Exact active scheduled-task prompt for weekly strategic brief and monthly red-team review. | Imported from active automation on 2026-07-08. |

## Canonicality rule

Save the reusable system logic here. Do not save every daily alert unless it changes the model, scoring rubric, or task design.

## Current caution

The recovered automation prompts include instructions to send email, but the automation metadata at recovery showed `notifications_enabled: false` and `email_enabled: false`. Treat the files here as canonical prompt/spec source; delivery settings must be verified in the ChatGPT automation UI when operational delivery matters.
