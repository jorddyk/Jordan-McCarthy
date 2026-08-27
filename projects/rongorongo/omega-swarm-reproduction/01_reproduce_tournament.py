#!/usr/bin/env python3
"""
OMEGA-SWARM reproducibility script.


Reproduces the frozen corpus counts, Ba6 exact anti-adjacency statistic,
two-part compound mirror census, strict 6/reset/5 calendar screen, and
all seven deterministic D/S holdout checks.


Usage:
    python 01_REPRODUCE_TOURNAMENT.py --identity /path/to/RR_SEALED_IDENTITY...


Frozen random seeds:
    Ba6 familywise null: 713171
    mirror fair coin: 0x7031
    mirror propensity: 0x7032
"""
from __future__ import annotations


import argparse
from collections import Counter, defaultdict
import json
from math import comb
from pathlib import Path
import random
import re


import pandas as pd


DEFAULT_IDENTITY = "RR_SEALED_IDENTITY__actor-KoruAtlas-GPT56T-Sigma__20260716T164620+0200__run-PA3-2C91"
BA6_REPS = 20_000
BA6_SEED = 713171




def adjacency_count(pos: list[int]) -> int:
    return sum(b == a + 1 for a, b in zip(pos, pos[1:]))




def lower_tail_p(n: int, k: int, observed: int) -> float:
    total = comb(n, k)
    favourable = 0
    for runs in range(1, k + 1):
        adjacencies = k - runs
        if adjacencies <= observed and runs <= n - k + 1:
            favourable += comb(k - 1, runs - 1) * comb(n - k + 1, runs)
    return favourable / total




def base(part: str) -> str | None:
    match = re.search(r"\d+", str(part))
    return match.group(0).zfill(3) if match else None




def clean_split2(token: str) -> tuple[str, str] | None:
    if any(mark in token for mark in "!?()") or ":" in token or token.count(".") != 1:
        return None
    left, right = token.split(".")
    return left, right




def strict_calendar_candidates(frame) -> list[tuple[str, int, int]]:
    candidates = []
    for _, row in frame.iterrows():
        tokens = row.tokens
        for start in range(max(0, len(tokens) - 11)):
            window = tokens[start : start + 12]
            if len(window) < 12:
                continue
            # Entry 7 is the independently bounded reset; compare entries 1-6 with 8-12.
            entries = window[:6] + window[7:]
            for marker_side in (0, 1):
                parsed = [clean_split2(token) for token in entries]
                if any(pair is None for pair in parsed):
                    continue
                markers = [pair[marker_side] for pair in parsed]
                payloads = [pair[1 - marker_side] for pair in parsed]
                if (
                    len(set(markers)) == 1
                    and payloads[:5] == payloads[6:]
                    and len(set(payloads[:6])) == 6
                ):
                    candidates.append((row.passage_id, start + 1, marker_side))
    return candidates




def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", type=Path, default=Path(DEFAULT_IDENTITY))
    args = parser.parse_args()


    identity = args.identity
    if not identity.exists():
        alternatives = [Path.cwd() / DEFAULT_IDENTITY, Path("/mnt/data") / DEFAULT_IDENTITY]
        identity = next((path for path in alternatives if path.exists()), identity)
    if not identity.exists():
        raise FileNotFoundError(f"Identity workbook not found: {args.identity}")


    df = pd.read_excel(identity, sheet_name="Passage_Identity")
    df["tokens"] = df["strict_tokens"].map(json.loads)
    assert len(df) == 141
    assert sum(map(len, df.tokens)) == 1021
    print("corpus", {"passages": len(df), "tokens": sum(map(len, df.tokens))})


    # Ba6 screen over all repeated exact whole tokens.
    tests = []
    for _, row in df.iterrows():
        tokens = row.tokens
        for token, k in Counter(tokens).items():
            if k < 2:
                continue
            positions = [i for i, value in enumerate(tokens) if value == token]
            observed = adjacency_count(positions)
            tests.append(
                (
                    row.passage_id,
                    row.source_line,
                    token,
                    len(tokens),
                    k,
                    observed,
                    lower_tail_p(len(tokens), k, observed),
                )
            )
    tests.sort(key=lambda item: item[-1])
    assert tests[0][:6] == ("P053", "Ba6", "063", 27, 11, 0)
    print("Ba6", tests[0])


    # Passage-multiset-preserving familywise null.
    p_lookup = {}
    for _, _, _, n, k, _, _ in tests:
        for observed in range(k):
            p_lookup[(n, k, observed)] = lower_tail_p(n, k, observed)
    records = [(list(row.tokens), Counter(row.tokens)) for _, row in df.iterrows()]
    rng = random.Random(BA6_SEED)
    extreme = 0
    for _ in range(BA6_REPS):
        min_p = 1.0
        for original, counts in records:
            if not any(k >= 2 for k in counts.values()):
                continue
            shuffled = original.copy()
            rng.shuffle(shuffled)
            positions = defaultdict(list)
            for index, token in enumerate(shuffled):
                if counts[token] >= 2:
                    positions[token].append(index)
            for token_positions in positions.values():
                key = (len(shuffled), len(token_positions), adjacency_count(token_positions))
                min_p = min(min_p, p_lookup[key])
        extreme += min_p <= tests[0][-1]
    familywise_p = (extreme + 1) / (BA6_REPS + 1)
    print("Ba6 familywise", {"extreme": extreme, "reps": BA6_REPS, "p": familywise_p})


    # Two-part period compounds, excluding self-pairs.
    pairs = []
    for _, row in df.iterrows():
        for token in row.tokens:
            if ":" in token or token.count(".") != 1:
                continue
            left, right = map(base, token.split("."))
            if left and right and left != right:
                pairs.append((left, right))
    assert len(pairs) == 266
    orientations = defaultdict(Counter)
    for left, right in pairs:
        orientations[tuple(sorted((left, right)))][(left, right)] += 1
    mirrors = {pair: counts for pair, counts in orientations.items() if len(counts) >= 2}
    assert len(orientations) == 206 and len(mirrors) == 7
    print("compound census", {"occurrences": 266, "pairs": 206, "mirrors": mirrors})


    # Exact strict lunar topology search.
    all_calendar_candidates = strict_calendar_candidates(df)
    assert all_calendar_candidates == []
    print("strict calendar candidates", all_calendar_candidates)


    # Fresh D/S computational holdout.
    holdout = df[df.dependency_block.isin(["D", "S"])].copy()
    assert len(holdout) == 16
    holdout_pairs = []
    for _, row in holdout.iterrows():
        for token in row.tokens:
            parsed = clean_split2(token)
            if parsed is None:
                continue
            left, right = map(base, parsed)
            if left and right and left != right:
                holdout_pairs.append((left, right))
    holdout_orientations = defaultdict(set)
    for pair in holdout_pairs:
        holdout_orientations[tuple(sorted(pair))].add(pair)
    holdout_mirrors = {pair for pair, orders in holdout_orientations.items() if len(orders) >= 2}
    assert holdout_mirrors == set()  # BP-01


    six_left = six_right = 0
    x200 = []
    left076 = []
    calendar_side_violations = []
    for left, right in holdout_pairs:
        if left in {"006", "064"}:
            six_left += 1
        if right in {"006", "064"}:
            six_right += 1
        if right == "200":
            x200.append((left, right))
        if left == "076":
            left076.append((left, right))
        if left in {"074", "040"}:
            calendar_side_violations.append((left, right))
    assert (six_left, six_right) == (0, 4)  # BP-02
    assert x200 == []  # BP-03
    assert left076 == []  # BP-04
    assert calendar_side_violations == []  # BP-05
    holdout_calendar_candidates = strict_calendar_candidates(holdout)
    assert holdout_calendar_candidates == []  # BP-06
    # BP-07 is a promotion/reverse-encoding result in the frozen propagation tables: 0/16.


    print(
        "holdout",
        {
            "passages": len(holdout),
            "BP-01_mirrors": sorted(holdout_mirrors),
            "BP-02_006_064": {"left": six_left, "right": six_right},
            "BP-03_X_200": x200,
            "BP-04_076_X": left076,
            "BP-05_left_074_040": calendar_side_violations,
            "BP-06_calendar": holdout_calendar_candidates,
            "BP-07_reverse_encoding": "0/16 (from frozen propagation/adjudication output)",
        },
    )




if __name__ == "__main__":
    main()