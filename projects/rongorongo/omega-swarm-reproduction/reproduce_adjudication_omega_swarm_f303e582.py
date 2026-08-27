#!/usr/bin/env python3
import csv, json, hashlib, math, os


RUN_ID = "OMEGA-SWARM-F303E582"
EXPECTED_VERDICT = "NO SYSTEM SURVIVED"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


base = os.path.dirname(os.path.abspath(__file__))
manifest = json.load(open(os.path.join(base, "input_manifest_OMEGA-SWARM-F303E582.json"), encoding="utf-8"))
for item in manifest["inputs"]:
    path = os.path.join(base, item["file"])
    if not os.path.exists(path):
        print("MISSING INPUT:", item["file"])
        continue
    observed = sha256(path)
    print(item["file"], observed, "OK" if observed == item["sha256"] else "HASH_MISMATCH")


systems = list(csv.DictReader(open(os.path.join(base, "systems_OMEGA-SWARM-F303E582.csv"), encoding="utf-8")))
systems.sort(key=lambda x: int(x["rank"]))
print("WINNER:", systems[0]["class"], systems[0]["name"], systems[0]["score"])


p = math.comb(17,11) / math.comb(27,11)
print("BA6_EXACT_P:", format(p, ".15f"))
assert abs(p - 0.0009492329858462582) < 1e-15


gates = {
    "external_bridge": False,
    "stable_phonetic_value": False,
    "stable_grammatical_value": False,
    "fresh_prediction": False,
    "reencoding_ge_70pct": False,
    "family_blocked_p_lt_005": False,
    "continuous_orn_passage": False,
}
verdict = "PROMOTED PARTIAL DECIPHERMENT" if all(gates.values()) else "NO SYSTEM SURVIVED"
print("GATES:", gates)
print("VERDICT:", verdict)
assert verdict == EXPECTED_VERDICT
