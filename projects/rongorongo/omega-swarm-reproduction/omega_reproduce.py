#!/usr/bin/env python3
"""Reproduce core OMEGA adjudication checks from the machine-readable CSV package."""
import csv, json, math, re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_csv(name):
    with open(ROOT / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


atlas = read_csv("passage_atlas_frozen.csv")
assert len(atlas) == 141
all_tokens = []
by_id = {}
for row in atlas:
    tokens = json.loads(row["strict_tokens"])
    by_id[row["passage_id"]] = tokens
    all_tokens.extend(tokens)
assert len(all_tokens) == 1021


ba6 = by_id["P053"]
positions = [i + 1 for i, x in enumerate(ba6) if x == "063"]
adjacency = sum(b == a + 1 for a, b in zip(positions, positions[1:]))
p_single = math.comb(17, 11) / math.comb(27, 11)
assert (len(ba6), len(positions), adjacency) == (27, 11, 0)


def base(part):
    groups = re.findall(r"\d+", part)
    return "".join(groups) if groups else None


pairs = []
for token in all_tokens:
    if ":" in token:
        continue
    parts = token.split(".")
    if len(parts) != 2:
        continue
    a, b = base(parts[0]), base(parts[1])
    if a and b and a != b:
        pairs.append((a, b))
assert len(pairs) == 266


unord = defaultdict(Counter)
for a, b in pairs:
    unord[tuple(sorted((a, b)))][(a, b)] += 1
mirrors = []
for key, counts in unord.items():
    a, b = key
    if counts[(a, b)] and counts[(b, a)]:
        mirrors.append((key, counts[(a, b)], counts[(b, a)]))
assert len(unord) == 206 and len(mirrors) == 7


side = defaultdict(lambda: [0, 0])
for a, b in pairs:
    side[a][0] += 1
    side[b][1] += 1


expected = {
    "006": (2,25), "003": (4,24), "200": (13,0), "076": (0,10),
    "074": (0,8), "052": (0,8), "711": (0,7), "022": (9,1),
    "300": (9,1), "306": (6,0), "001": (12,12), "010": (10,11),
    "600": (7,6), "005": (6,5), "004": (16,8),
}
for sign, counts in expected.items():
    assert tuple(side[sign]) == counts


print("PASS: frozen passages =", len(atlas))
print("PASS: whole tokens =", len(all_tokens))
print("PASS: Ba6 free-063 positions =", positions)
print("PASS: Ba6 adjacent 063 pairs =", adjacency)
print("PASS: Ba6 exact p =", p_single)
print("PASS: qualifying compounds =", len(pairs))
print("PASS: unordered compound pairs =", len(unord))
print("PASS: mirror-capable pairs =", sorted(mirrors))
print("PASS: side counts reproduce exactly")
print("VERDICT: NO SYSTEM SURVIVED")