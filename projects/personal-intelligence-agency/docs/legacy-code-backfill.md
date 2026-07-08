# Personal Intelligence Agency Legacy Backfill

Status date: 2026-07-08

This file tracks recovered prompt/spec artifacts and remaining source-recovery targets for Jordan's personal intelligence agency automation system. It is not a daily report output archive.

## Imported exact scheduled-task prompts

Recovered from active ChatGPT automations during the 2026-07-08 legacy code backfill:

| Canonical path | Source title | Timing mode | Data status |
|---|---|---|---|
| `projects/personal-intelligence-agency/prompts/code-handoff.md` | Code Handoff | flexible_schedule | Exact prompt/spec artifact; no raw private data; not runnable code. |
| `projects/personal-intelligence-agency/prompts/strategic-alert-triage.md` | Strategic Alert Triage | condition_watch | Exact prompt/spec artifact; no raw private data; not runnable code. |
| `projects/personal-intelligence-agency/prompts/science-preemption-watch.md` | Science Preemption Watch | flexible_schedule | Exact prompt/spec artifact; no raw private data; not runnable code. |
| `projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md` | Swiss Leverage Radar | flexible_schedule | Exact prompt/spec artifact; no raw private data; not runnable code. |
| `projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md` | Strategic Brief Redteam | flexible_schedule | Exact prompt/spec artifact; no raw private data; not runnable code. |

## Recovery notes

- The prompts were imported as project-organized canonical source under `projects/personal-intelligence-agency/prompts/`, not under daily handoff folders.
- Each file includes recovery metadata, schedule metadata at recovery, and the exact recovered prompt body.
- The recovered automation metadata showed `notifications_enabled: false` and `email_enabled: false` for all listed tasks. The prompt files preserve task logic; operational delivery settings must be verified separately in the ChatGPT automation UI when delivery matters.

## Remaining targets

| Target | Proposed path | Status |
|---|---|---|
| 0-to-21 strategic signal scoring rubric | `projects/personal-intelligence-agency/rubrics/strategic-signal-score-0-to-21.md` | Exact full rubric not yet recovered; do not reconstruct unless source is found or Jordan asks for a new rubric. |
| Alert email/report templates | `projects/personal-intelligence-agency/reports/` | Exact templates not yet recovered beyond prompt descriptions. |
| Historical task outputs | `docs/handoffs/` or project reports only when strategy changed | Not imported; daily/weekly generated outputs are not canonical source unless they change reusable logic. |

## Integrity rule

Do not commit raw private Gmail/calendar contents, full personal dossiers, or transient daily alert outputs here. Store reusable task logic, scoring rubrics, and report templates only.
