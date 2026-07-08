# Strategic Alert Triage

## Recovery metadata

- Human purpose: Daily condition-watch prompt for urgent strategic alerts affecting Jordan's thesis, JM105/Intronsaurus, ETH/Barral lab spinout options, funding, career, housing/assets, and high-value personal-source items.
- Original source clue/conversation context: Recovered exactly from active ChatGPT scheduled task `Strategic Alert Triage` during the 2026-07-08 legacy code backfill.
- Expected inputs: Lawful public sources plus Jordan-authorized personal sources available to ChatGPT, including project context, memory, Gmail, Google Calendar, Google Drive, GitHub, contacts, and connected sources where available.
- Expected outputs: Notification/email only when a threshold signal exists; otherwise no notification.
- Known assumptions: Uses an intelligence-cycle structure, signal scoring from 0 to 21, and a thin self-counterintelligence layer only when it changes the recommended action.
- Data status: Prompt/spec artifact only. No biological data, no private inbox/calendar dump, no generated analysis output.

## Schedule metadata at recovery

```text
Title: Strategic Alert Triage
Timing mode: condition_watch
Schedule:
BEGIN:VEVENT
DTSTART:20260708T080000
RRULE:FREQ=DAILY
END:VEVENT
Notifications enabled: false
Email enabled: false
```

## Exact recovered prompt

```text
Run Jordan McCarthy's daily strategic alert triage. Check for urgent changes affecting thesis execution, JM105/Intronsaurus, ETH/Barral lab spinout options, funding deadlines, high-value emails/calendar items, Google Drive/project artifacts, Swiss career leverage, and Zürich asset/housing opportunities. Use only lawful public sources and Jordan-authorized personal sources, including available ChatGPT/project context, memory, Gmail, Google Calendar, Google Drive, GitHub, contacts, and other connected sources where access is available.

Use an intelligence-cycle structure: requirements -> collection -> relevance filtering -> analysis -> action/no action. Notify Jordan only if there is an item requiring action within the next 7 days, a deadline risk, a high-value unanswered message, a major opportunity, or a strategic threat.

Add a thin self-counterintelligence layer without letting it dominate: ask whether Jordan's current behavior or information environment is likely to block action on the alert. Check for avoidance, over-analysis, perfectionism, ignored messages, calendar conflicts, stale assumptions, excessive context switching, unrealistic workload, or money/career drift. Include this only if it directly changes the recommended action. Do not produce self-analysis for its own sake.

Separate facts, inference, and speculation; cite sources; score each signal 0-21; end with act, wait, watch, ask, apply, contact, publish, stop, or no action. If nothing meets the threshold, do not notify and do not send email. If something meets the threshold, send Jordan an email at jordymac18@gmail.com with subject "Strategic alert: [brief signal]" and a concise body containing the alert, source citations/links, signal score, recommended action, deadline/time sensitivity, and any relevant self-counterintelligence blocker plus the smallest containment action.
```
