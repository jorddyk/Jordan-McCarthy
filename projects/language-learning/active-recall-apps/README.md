# Active Recall Web Apps

Human goal: preserve runnable, single-file language-learning web apps that Jordan can open locally or on a phone.

## Canonical naming convention

Use names that describe the app's purpose, not when it was created.

Good:

- `kartoffel-vocabulary-active-recall.html`
- `telc-c1-essay-skeleton-active-recall.html`
- `b1-german-wordlist-flashcards.html`

Bad:

- `german-drill-6.html`
- `final.html`
- `working.html`
- `chatgpt_version.html`

## Candidate imports

### Kartoffel Vocabulary Active Recall

Proposed path: `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`

Purpose: English-to-German vocabulary training from a Kartoffel text. The visible source includes a mobile-first single-page HTML app with typed German answers, aliases, reveal/check/next controls, missed pile, shuffle, loop, and adjustable pause. Full source is required before committing.

### TELC C1 Essay Skeleton Active Recall

Proposed path: `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`

Purpose: active recall for reusable TELC C1 essay phrases. The visible source includes a mobile-first single-page HTML app with English cue, timed gap, German answer reveal, progress bar, loop/restart, and pause controls. Full source is required before committing.

## Canonicality checklist

A candidate app may be committed when:

- The full source is available, not truncated.
- The file starts with `<!DOCTYPE html>` and ends with `</html>`.
- The app has a human title in the `<title>` tag.
- The purpose is documented in this README.
- No unrelated private text or hidden scratch content is embedded.
