# Language-Learning Apps

Human goal: preserve small useful language-learning tools Jordan built with ChatGPT, especially German/TELC active-recall web apps.

This project is for runnable study tools, not raw PDFs or study-source documents.

## Subprojects

| Folder | Human title | What it does |
|---|---|---|
| `active-recall-apps/` | Active recall web apps | Single-file HTML/JS/CSS apps for German vocabulary, TELC C1 phrases, and oral recall drills |

## Canonical apps

| Path | Source recovered from | Goal | Status |
|---|---|---|---|
| `active-recall-apps/kartoffel-vocabulary-active-recall.html` | File Library artifact `kartoffel_vocabulary_active_recall_WORKING.html`, recovered as complete source from `<!DOCTYPE html>` through `</html>` on 2026-07-09 | English-to-German Kartoffel-text vocabulary trainer with aliases, missed pile, shuffle/loop controls, timer ring, and typo tolerance | Canonical runnable single-file HTML app |

## Current source candidates awaiting full-code import

| Candidate source name | Proposed canonical file | Goal | Status |
|---|---|---|---|
| `german-drill-6.html` | `active-recall-apps/telc-c1-essay-skeleton-active-recall.html` | TELC C1 essay-skeleton phrase drill with spoken prompt, timed gap, answer reveal, loop/restart controls | Pending exact full source recovery |

## Import rule

Do not commit partial/truncated HTML. A web app is canonical only when the complete file from `<!DOCTYPE html>` through `</html>` is available and runnable.
