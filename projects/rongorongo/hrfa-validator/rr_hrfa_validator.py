#!/usr/bin/env python3
from pathlib import Path
import csv, json, re

ROOT = Path(__file__).resolve().parent
ATLAS = ROOT / "formula_atlas.jsonl"
OUT = ROOT / "anonymous_structures.regenerated.csv"

HEADERS = ["anonymous_record_id", "entry_count", "clause_count", "framing_code", "fixed_position_count", "variable_position_count", "optional_position_count", "slot_order_code", "slot_length_distribution_code", "repeated_payload_count", "rolling_reuse_flag", "endpoint_asymmetry_flag", "omission_code", "expansion_code", "reset_code", "final_member_alteration_flag", "terminal_formula_flag", "refrain_subtype_code", "dependency_code", "source_block_independence_count", "specificity_score", "prediction_risk_score", "specificity_band_code", "risk_band_code", "falsifier_status_code"]
SLOT = {"HRF001": "F1>V1||F1>V2", "HRF002": "O1?>V1×N", "HRF003": "F1>V1>F2>V2?×3", "HRF004": "F1>V1×3[P0,P0,P1]", "HRF005": "F1>V1>F2×3;T1", "HRF006": "F1>V1×2", "HRF007": "F1>V1;F1>V2", "HRF008": "V1>F1>V2;V2>F1>V3…", "HRF009": "F1>V1||F2>V2", "HRF010": "F1>V1>F2>V2>F3>V3>T1", "HRF011": "V1(2)>F1>V2", "HRF012": "F1>V1||F1>V2", "HRF013": "F1>V1>F2", "HRF014": "F1>V1+V2+V3>F2", "HRF015": "V1+V2>F1>F2", "HRF016": "P1>V1×12–13", "HRF017": "F1>R1>F2>R2>F3", "HRF018": "C1..C6>F1>C1..C5", "HRF019": "V1>F1>V1>F2>V1", "HRF020": "F1>F2>V1", "HRF021": "F1>F2", "HRF022": "V1(N)>F1>R1>V1(SUBSET)", "HRF023": "F1>V1||F2>V2", "HRF024": "F1>V1>F2×N;T1", "HRF025": "F1>V1||F1>V2[REV]", "HRF026": "V1+V2+V3+V4>F1>F2>T1", "HRF027": "F1>V1(4)||F2>V2(5)", "HRF028": "F1>F2>V1>T1", "HRF029": "F1>F2>F3>F4>F5>F6>F7>F8…", "HRF030": "V1>V2>V3", "HRF031": "F1>V1", "HRF032": "V1>V2>V3"}
LENGTH = {"HRF001": "L1/L1", "HRF002": "L1×N", "HRF003": "L3-5×3", "HRF004": "L2×3", "HRF005": "L2-4×3+LT", "HRF006": "L2×2", "HRF007": "L2-3×2", "HRF008": "L2-4×N", "HRF009": "L2-3×2", "HRF010": "LMIX", "HRF011": "L1-3", "HRF012": "L2-3×2", "HRF013": "L2-4×3", "HRF014": "LMIX", "HRF015": "LMIX", "HRF016": "L1-2×N", "HRF017": "L1-2×N", "HRF018": "L2×11", "HRF019": "L1-3×N", "HRF020": "L2-5", "HRF021": "L3", "HRF022": "LMIX", "HRF023": "L2-4×2", "HRF024": "L3-6×N", "HRF025": "L2-5×2", "HRF026": "L1×4+L1-4", "HRF027": "L4/L5", "HRF028": "L2-6×3", "HRF029": "LMIX", "HRF030": "L2×3", "HRF031": "L2", "HRF032": "L1-3×3"}
OMIT = {"HRF001": "O00", "HRF002": "O_VAR_MID", "HRF003": "O_M1_M2", "HRF004": "O00", "HRF005": "O00", "HRF006": "O00", "HRF007": "O_OPT_A", "HRF008": "O_OPT_NODE", "HRF009": "O_OPT_SCOPE", "HRF010": "O_OPT_AUX", "HRF011": "O_OPT_MEMBER", "HRF012": "O00", "HRF013": "O00", "HRF014": "O_OPT_SET", "HRF015": "O_OPT_SET", "HRF016": "O_OPT_CYCLE", "HRF017": "O_OPT_1_2", "HRF018": "O_RUN2_POS6", "HRF019": "O_OPT_A", "HRF020": "O_OPT_A", "HRF021": "O00", "HRF022": "O_OPT_1", "HRF023": "O_OPT_SET", "HRF024": "O00", "HRF025": "O_OPT_A", "HRF026": "O_OPT_A", "HRF027": "O00", "HRF028": "O_OPT_A", "HRF029": "O_OPT_BRANCH", "HRF030": "O00", "HRF031": "O00", "HRF032": "O00"}
EXPAND = {"HRF001": "E00", "HRF002": "E_VAR_N", "HRF003": "E_M3", "HRF004": "E_M3_REV", "HRF005": "E_T", "HRF006": "E00", "HRF007": "E_M2", "HRF008": "E_NODE", "HRF009": "E00", "HRF010": "E_AUX", "HRF011": "E_PAIR_COMPRESS", "HRF012": "E00", "HRF013": "E_T_REV", "HRF014": "E_SET", "HRF015": "E_SET", "HRF016": "E_PAIR_MOD", "HRF017": "E_INSERT", "HRF018": "E00", "HRF019": "E_STAGE", "HRF020": "E_T_OPT", "HRF021": "E00", "HRF022": "E_ROUTE", "HRF023": "E00", "HRF024": "E_T_RESOLVE", "HRF025": "E_M2", "HRF026": "E_T", "HRF027": "E_M2_PLUS1", "HRF028": "E_T", "HRF029": "E_BRANCH", "HRF030": "E00", "HRF031": "E00", "HRF032": "E_M3_OPT"}
RESET = {"HRF001": "R00", "HRF002": "R00", "HRF003": "R00", "HRF004": "R00", "HRF005": "R00", "HRF006": "R00", "HRF007": "R00", "HRF008": "R_ROUTE?", "HRF009": "R00", "HRF010": "R00", "HRF011": "R00", "HRF012": "R00", "HRF013": "R00", "HRF014": "R00", "HRF015": "R00", "HRF016": "R_CYCLE", "HRF017": "R_CYCLE", "HRF018": "R_AFTER_F1", "HRF019": "R_CYCLE", "HRF020": "R00", "HRF021": "R00", "HRF022": "R_END", "HRF023": "R00", "HRF024": "R00", "HRF025": "R00", "HRF026": "R00", "HRF027": "R00", "HRF028": "R00", "HRF029": "R_CYCLE", "HRF030": "R_STAGE", "HRF031": "R00", "HRF032": "R00"}
REFRAIN = {"NONE": "RF00", "CALL_RESPONSE": "RF01", "RESPONSORIAL_POSSIBLE": "RF02", "ANTITHETIC": "RF03", "TERMINAL": "RF04", "INVOCATION": "RF05", "RESPONSORIAL": "RF06"}

BANNED_HEADERS = {
    "family_id","family_label","historical_layer","source_blocks","witness_summary",
    "collector","informant","genre","period","translation","diplomatic_transcription",
    "source_block_id","source_url","source_locator"
}
BANNED_TERMS = {
    "routledge","thomson","métraux","metraux","roussel","rapa nui","genealogy",
    "calendar","ritual","royal","migration","birdman","chant","modern","collector","informant"
}

records = [json.loads(x) for x in ATLAS.read_text(encoding="utf-8").splitlines() if x.strip()]
rows = []
for i, r in enumerate(records, 1):
    fid = r["family_id"]
    rows.append([
        f"AF{i:04d}", r["entry_count"], r["clause_count"], r["framing"],
        r["fixed_position_count"], r["variable_position_count"], r["optional_position_count"],
        SLOT[fid], LENGTH[fid], r["repeated_payload_count"], r["rolling_reuse"],
        r["endpoint_asymmetry"], OMIT[fid], EXPAND[fid], RESET[fid],
        r["final_member_alteration"], r["terminal_formula"], REFRAIN.get(r["refrain_subtype"], "RF99"),
        f"D{i:02d}", r["source_block_independence_count"], r["specificity_score_1_10"],
        r["prediction_risk_1_10"], f"S{r['specificity_score_1_10']}",
        f"R{r['prediction_risk_1_10']}", "FALSIFIER_PRESENT"
    ])

bad_headers = [h for h in HEADERS if h.lower() in BANNED_HEADERS]
if bad_headers:
    raise SystemExit(f"Banned headers: {bad_headers}")
for row_number, row in enumerate(rows, 2):
    joined = " ".join(map(str, row)).lower()
    hits = sorted(t for t in BANNED_TERMS if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", joined))
    if hits:
        raise SystemExit(f"Banned values at row {row_number}: {hits}")
if any(row[-1] != "FALSIFIER_PRESENT" for row in rows):
    raise SystemExit("Missing falsifier status.")

with OUT.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(HEADERS)
    w.writerows(rows)
print(f"validated_records={len(records)}")
print(f"anonymized_rows={len(rows)}")
print(f"output={OUT}")
