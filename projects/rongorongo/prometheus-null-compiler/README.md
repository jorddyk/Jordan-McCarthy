# PROMETHEUS-SWARM null bidirectional compiler

Recovered verbatim from Google Drive doc "06_EXECUTABLE_NULL_COMPILER_SOURCE_AND_HASHES — PROM-JM-9F3C" (id `1oQ78bK-uc0BQ9jfh1o7r6xwxY4sQTTpbWl-Vz9aWJLg`, modified 2026-07-17), run ID `PROM-JM-9F3C`, verdict `NO AUTHENTIC BRIDGE SURVIVED`.

## What it does

A CLI (`analyze` / `decode` / `encode` / `self-test`) that intentionally **refuses** to translate between Rongorongo glyph tokens and Old Rapa Nui, because the authoritative sign-value ledger contains zero promoted phonetic, lexical, or grammatical values. `decode()` and `encode()` both always return `status="UNSUPPORTED"`, `confidence=0.0`. What it *will* do is expose structure that needs no linguistic interpretation: strict token parsing, first-occurrence equality-class patterns, exact repeated contiguous spans, and compound-attachment geometry (period/colon component splits).

It explicitly hard-codes five specific sign readings it refuses to promote (`003=rongo`, `006=a/ki/particle`, `076=person/name marker`, `078=ure/lineage`, `200=ko/particle`) as `FORBIDDEN_ASSIGNMENTS` — these were rejected candidate readings from the broader adjudication, kept here as a guardrail against accidentally reintroducing them.

## Status: RECOVERED and independently validated — runnable as-is

Unlike the other scripts in `projects/rongorongo/`, this one has no external data dependency. It was:

- extracted byte-for-byte from a plain-text/base64 Drive export (not the markdown view, to avoid escaping corruption of `<`, `>`, `#!`, etc.);
- compiled clean (`python -m py_compile`);
- **actually executed** (`python rr_prometheus_compiler.py self-test`) — output matched the self-test result recorded in the source document exactly:

```json
{
  "status": "PASS",
  "tests": 4,
  "run_id": "PROM-JM-9F3C",
  "verdict": "NO AUTHENTIC BRIDGE SURVIVED"
}
```

Usage:

```
python rr_prometheus_compiler.py analyze "380 001 380 001 280.076"
python rr_prometheus_compiler.py decode "380 001"
python rr_prometheus_compiler.py encode "he kupu"
python rr_prometheus_compiler.py self-test
```

## Not included

The source document also recorded a SHA-256 table for four sibling package files (`README.md`, `manifest.json`, `promotion_criteria.csv`, `self_test.json`) whose contents were not embedded in the document, so they are not reconstructed here.
