#!/usr/bin/env python3
"""
PROMETHEUS-SWARM structural analyzer and null bidirectional compiler.


This executable intentionally refuses linguistic decoding/encoding because the
authoritative sign-value ledger contains zero promoted phonetic, lexical, or
grammatical values. It preserves strict token ontology and exposes only
structure that is independently supported.
"""
from __future__ import annotations


from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from typing import Iterable
import argparse
import json
import re
import sys


RUN_ID = "PROM-JM-9F3C"
VERDICT = "NO AUTHENTIC BRIDGE SURVIVED"


FORBIDDEN_ASSIGNMENTS = {
    "003": "rongo",
    "006": "a / ki / grammatical particle",
    "076": "person or name marker",
    "078": "ure or lineage",
    "200": "ko or grammatical particle",
}


TOKEN_RE = re.compile(r"^[0-9A-Za-z?]+(?:[.:][0-9A-Za-z?]+)*$")




@dataclass(frozen=True)
class CompilerResult:
    direction: str
    status: str
    input: object
    output: object
    confidence: float
    reason: str
    run_id: str = RUN_ID
    verdict: str = VERDICT


    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)




def parse_token_stream(text: str) -> list[str]:
    """Parse whitespace/hyphen-separated strict whole or fused tokens."""
    raw = [piece for piece in re.split(r"[\s\-]+", text.strip()) if piece]
    invalid = [token for token in raw if not TOKEN_RE.match(token)]
    if invalid:
        raise ValueError(f"Invalid strict token(s): {invalid}")
    return raw




def equality_pattern(tokens: Iterable[str]) -> list[int]:
    """Map exact token equality to first-occurrence integer classes."""
    classes: dict[str, int] = {}
    out: list[int] = []
    for token in tokens:
        if token not in classes:
            classes[token] = len(classes)
        out.append(classes[token])
    return out




def repeated_spans(tokens: list[str], min_len: int = 2) -> list[dict]:
    """Return exact repeated contiguous spans without assigning meaning."""
    spans: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    n = len(tokens)
    for length in range(min_len, n // 2 + 1):
        for start in range(0, n - length + 1):
            spans[tuple(tokens[start : start + length])].append(start)
    return [
        {"span": list(span), "starts": starts, "count": len(starts)}
        for span, starts in spans.items()
        if len(starts) > 1
    ]




def attachment_geometry(token: str) -> dict:
    """Describe compound separators without inferring spoken order."""
    return {
        "token": token,
        "period_components": token.split("."),
        "colon_components": token.split(":"),
        "has_period_attachment": "." in token,
        "has_colon_attachment": ":" in token,
    }




def analyze(text: str) -> dict:
    tokens = parse_token_stream(text)
    counts = Counter(tokens)
    return {
        "run_id": RUN_ID,
        "verdict": VERDICT,
        "strict_tokens": tokens,
        "token_count": len(tokens),
        "type_count": len(counts),
        "equality_pattern": equality_pattern(tokens),
        "repeated_tokens": {k: v for k, v in counts.items() if v > 1},
        "repeated_spans": repeated_spans(tokens),
        "geometry": [attachment_geometry(t) for t in tokens],
        "linguistic_values_assigned": 0,
    }




def decode(text: str) -> CompilerResult:
    analysis = analyze(text)
    return CompilerResult(
        direction="Rongorongo tokens → Old Rapa Nui",
        status="UNSUPPORTED",
        input=analysis,
        output=None,
        confidence=0.0,
        reason=(
            "No authentic bridge or promoted sign value exists. "
            "Returning Old Rapa Nui wording would introduce values after inspection."
        ),
    )




def encode(text: str) -> CompilerResult:
    normalized = " ".join(text.split())
    if not normalized:
        raise ValueError("Old Rapa Nui input must not be empty.")
    return CompilerResult(
        direction="Old Rapa Nui → Rongorongo tokens",
        status="UNSUPPORTED",
        input=normalized,
        output=None,
        confidence=0.0,
        reason=(
            "No validated vocabulary, grammar, reading order, omission rule, "
            "or compound-construction mapping exists."
        ),
    )




def self_test() -> dict:
    sample = "380 001 380 001 280.076"
    parsed = analyze(sample)
    assert parsed["equality_pattern"] == [0, 1, 0, 1, 2]
    assert decode(sample).status == "UNSUPPORTED"
    assert encode("he kupu").status == "UNSUPPORTED"
    assert set(FORBIDDEN_ASSIGNMENTS) == {"003", "006", "076", "078", "200"}
    return {
        "status": "PASS",
        "tests": 4,
        "run_id": RUN_ID,
        "verdict": VERDICT,
    }




def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)


    for command in ("analyze", "decode", "encode"):
        p = sub.add_parser(command)
        p.add_argument("text")


    sub.add_parser("self-test")
    args = parser.parse_args(argv)


    try:
        if args.command == "analyze":
            print(json.dumps(analyze(args.text), ensure_ascii=False, indent=2))
        elif args.command == "decode":
            print(decode(args.text).to_json())
        elif args.command == "encode":
            print(encode(args.text).to_json())
        else:
            print(json.dumps(self_test(), indent=2))
    except ValueError as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, indent=2), file=sys.stderr)
        return 2
    return 0




if __name__ == "__main__":
    raise SystemExit(main())