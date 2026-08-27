"""
diagnose_classifier.py -- frame-level "what KERAS says vs what the human says" audit.

Run this ON THE WORKSTATION (needs the TIFF stacks on Y:\\ plus the same folder
as human_classifier_ui.py, the deployed model files and the master Excel).

    python diagnose_classifier.py                        # six-cond chip + sample of old chips
    python diagnose_classifier.py --chips JM135_SixCondition_33
    python diagnose_classifier.py --max-old-traps 0      # six-cond only, fastest

WHAT IT DOES
  1. PROVENANCE AUDIT -- identifies which model generation is actually deployed
     (the Aug-13 sweep-era single-head model vs. the endpoint-trained multitask
     model), what model_input_meta.json / class_labels.json / hmm_transitions.json
     currently say, and whether candidate_* files exist (i.e. the new trainer ran
     but its deployment gate FAILED, so production files were never replaced).
  2. FRAME-LEVEL CONFUSION -- runs the deployed model over every annotated trap
     using the UI's EXACT input builder and decoding chain (imported from
     human_classifier_ui.py, so nothing can silently diverge), then compares
     per-frame predictions against the human labels: confusion matrix per chip,
     per-class recall, confidence by true class, and specifically the fraction
     of human Early/Late Bud frames the model calls 'Mother'.
  3. EVENT/RLS AUDIT -- human vs. model division events (matched within a +/-2
     frame window, missed, spurious), per-trap RLS with BOTH decodings (raw
     argmax and the deployed Viterbi temperature), death-call agreement, and
     chip-stratified MAE/bias -- the numbers the HEARTH Round-12 gate asks for.
  4. DISAGREEMENT QUEUE -- frame_disagreements.csv listing the highest-confidence
     wrong frames (chip, position, trap, frame, human, model, confidence) so the
     worst offenders can be jumped to directly in the annotator UI.

Outputs land in ./diagnosis_out/.
"""

import os
import re
import sys
import json
import glob
import argparse
import datetime
import zipfile

import numpy as np
import pandas as pd
import tifffile as tif

# The UI module is the single source of truth for preprocessing + decoding.
# Importing it guarantees this audit sees exactly what the annotator sees.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import human_classifier_ui as ui  # noqa: E402  (imports cv2/tensorflow itself)

OUT_DIR = "diagnosis_out"
# Escape stays out of the confusion matrix only for legacy 6-class models;
# 7-class escape-aware models score it like any other state (see run-time
# adjustment where labels are loaded).
EXCLUDED_FROM_CONFUSION = {"Mother Escaped (Ignore Rest)", "Skipped / Bad Trap"}
ALPHABETICAL_SIX = ["Dead Cell", "Early Bud", "Late Bud", "Mother", "No Cell",
                    "Out of Focus / Blurry"]
ALPHABETICAL_SEVEN = ["Dead Cell", "Early Bud", "Late Bud", "Mother",
                      "Mother Escaped (Ignore Rest)", "No Cell",
                      "Out of Focus / Blurry"]

# Chip -> extracted-traps directory. Imported from the trainer when possible so
# the mapping can never fork; falls back to a local copy if that import fails.
try:
    from train_classifier import DEFAULT_TRAPS_DIRS  # noqa: E402
except Exception:
    DEFAULT_TRAPS_DIRS = {
        "JM135_CR_Mud1": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps",
        "JM135_CR_Mud1_Chip2_Intronless": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Aging Chip 2 includes intronless Mud1\_1\extracted_traps",
        "JM135_SixCondition_33": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Six condition chip\_33\extracted_traps",
    }


# ==============================================================================
# 1. PROVENANCE AUDIT
# ==============================================================================
def audit_provenance():
    print("=" * 78)
    print("PROVENANCE AUDIT -- which system is actually deployed?")
    print("=" * 78)
    problems = []

    model_path = ui.MODEL_PATH
    if not os.path.exists(model_path):
        print(f"[!] {model_path} not found next to this script -- run from the UI folder.")
        sys.exit(1)

    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(model_path))
    print(f"model file:            {model_path}  (mtime {mtime:%Y-%m-%d %H:%M})")
    try:
        with zipfile.ZipFile(model_path) as z:
            meta = json.loads(z.read("metadata.json"))
            cfg = json.loads(z.read("config.json"))
        layer_names = [L["config"].get("name", "") for L in cfg["config"]["layers"]]
        print(f"saved by Keras:        {meta.get('keras_version')}  on {meta.get('date_saved')}")
        if "motion_c1" in layer_names or "fused_features" in layer_names:
            print("architecture:          NEW endpoint-trained multitask state submodel")
        else:
            print("architecture:          OLD sweep-era single-head model "
                  "(input_rgb_heatmap -> adapter -> MobileNetV2 -> softmax)")
            problems.append(
                "Deployed aging_chip_classifier.keras is the PRE-REDESIGN (Aug-13) model. "
                "The endpoint-trained system never replaced it."
            )
    except Exception as e:
        print(f"(could not inspect .keras archive: {e})")

    if os.path.exists("model_input_meta.json"):
        with open("model_input_meta.json") as f:
            mim = json.load(f)
        print(f"model_input_meta.json: {mim}")
        if float(mim.get("viterbi_temperature", 1.0)) > 0:
            problems.append(
                f"Viterbi smoothing is ACTIVE at T={mim.get('viterbi_temperature')}. At the "
                "confidences this model produces (~35-45%), smoothing alone absorbs the "
                "1-2 frame Mother/Early interludes that define divisions (see RLS audit)."
            )
    else:
        print("model_input_meta.json: MISSING -> UI falls back to T=1.0 smoothing "
              "and prints an input-format warning.")
        problems.append("model_input_meta.json missing: UI smooths at fallback T=1.0.")

    if os.path.exists(ui.CLASS_LABELS_PATH):
        with open(ui.CLASS_LABELS_PATH) as f:
            labels = json.load(f)
        print(f"class_labels.json:     {labels}")
        if list(labels) == ALPHABETICAL_SEVEN:
            # Escape-aware 7-class model: score escape as a real state.
            EXCLUDED_FROM_CONFUSION.discard("Mother Escaped (Ignore Rest)")
        elif list(labels) != ALPHABETICAL_SIX:
            problems.append(
                f"class_labels.json ordering {labels} != expected alphabetical six "
                f"{ALPHABETICAL_SIX}: every prediction would be silently mislabeled."
            )
    else:
        problems.append("class_labels.json MISSING: UI shows 'Class N' and cannot smooth.")

    for f_ in ("aging_chip_rls_detector.keras", "rls_detector_meta.json"):
        print(f"{f_:22s} {'present' if os.path.exists(f_) else 'ABSENT'}")
    cands = sorted(glob.glob("candidate_*"))
    if cands:
        print("candidate_* files:     " + ", ".join(cands))
        problems.append(
            "candidate_* files exist -> the endpoint trainer ran but FAILED its deployment "
            "gate (test MAE <= 1.00), so production files were intentionally not replaced. "
            "Inspect candidate_rls_detector_meta.json / rls_test_concordance.csv."
        )
    print(
        "\nNOTE: the UI's 'Classifier Counted Trap RLS' is computed from STATE-model "
        "argmax/Viterbi labels only. aging_chip_rls_detector.keras (the calibrated "
        "division-event head) is NEVER consulted by the UI, so even a passing detector "
        "would not change the on-screen number without a UI change."
    )
    if problems:
        print("\n[!] PROVENANCE PROBLEMS:")
        for p in problems:
            print(f"    - {p}")
    return problems


# ==============================================================================
# 2 + 3. FRAME AND EVENT AUDIT
# ==============================================================================
def find_trap_file(chip, position, trap_id):
    root = DEFAULT_TRAPS_DIRS.get(chip)
    if root is None:
        return None
    pats = [os.path.join(root, f"{position}_trap_{trap_id}.tif"),
            os.path.join(root, "**", f"{position}_trap_{trap_id}.tif")]
    for p in pats:
        hits = glob.glob(p, recursive=True)
        if hits:
            return hits[0]
    # tolerate case / pos formatting differences
    for f_ in glob.glob(os.path.join(root, "**", "*.tif"), recursive=True):
        b = os.path.basename(f_)
        pm = re.search(r"(pos\d+)", b, re.IGNORECASE)
        tm = re.search(r"trap_?(\d+)\.tif", b, re.IGNORECASE)
        if pm and tm and pm.group(1).lower() == str(position).lower() and int(tm.group(1)) == int(trap_id):
            return f_
    return None


def coords_from_row(row):
    return {k: row.get(k, np.nan) for k in ui.SPATIAL_KEYS}


def run_trap(model, stack, coord_by_frame, transitions, temperature):
    """Model over the full stack with the UI's exact input builder; returns
    (probs, argmax_labels, smoothed_labels_or_None)."""
    inputs = []
    n = len(stack)
    for i in range(n):
        inputs.append(ui.build_model_input(
            stack[i],
            coords=coord_by_frame.get(i),
            prev_img=stack[i - 1] if i > 0 else None,
            next_img=stack[i + 1] if i + 1 < n else None,
        ))
    import tensorflow as tf
    logits = model.predict(np.asarray(inputs, dtype=np.float32), verbose=0)
    probs = tf.nn.softmax(logits).numpy()
    argmax_labels = [ui.CLASS_LABELS[i] for i in probs.argmax(axis=1)]
    smoothed_labels = None
    if temperature and temperature > 0 and transitions is not None:
        smooth_probs = tf.nn.softmax(logits / float(temperature)).numpy()
        path = ui.viterbi_smooth(smooth_probs, transitions)
        smoothed_labels = [ui.CLASS_LABELS[i] for i in path]
    return probs, argmax_labels, smoothed_labels


def match_events(human_ev, model_ev, window=2):
    """Greedy 1:1 matching of division frames within +/-window."""
    used = set()
    matched = 0
    for h in human_ev:
        best = None
        for j, m in enumerate(model_ev):
            if j in used or abs(m - h) > window:
                continue
            if best is None or abs(m - h) < abs(model_ev[best] - h):
                best = j
        if best is not None:
            used.add(best)
            matched += 1
    return matched, len(human_ev) - matched, len(model_ev) - len(used)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chips", nargs="*", default=None,
                    help="Chip_IDs to audit (default: all in the Excel)")
    ap.add_argument("--position", default=None, help="restrict to one position")
    ap.add_argument("--max-old-traps", type=int, default=12,
                    help="cap on traps sampled per NON-six-condition chip (0 = skip old chips)")
    ap.add_argument("--annotations", default=ui.MASTER_EXCEL_PATH)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    problems = audit_provenance()

    model = ui.load_keras_classifier(ui.MODEL_PATH)
    if model is None or not ui.CLASS_LABELS:
        sys.exit("[!] Model or class_labels.json unavailable -- cannot audit predictions.")
    transitions = ui.load_transition_matrix(ui.CLASS_LABELS)
    temperature = ui.VITERBI_TEMPERATURE
    if os.path.exists("model_input_meta.json"):
        try:
            with open("model_input_meta.json") as f:
                temperature = float(json.load(f).get("viterbi_temperature", temperature))
        except Exception:
            pass
    print(f"\nDecoding chains audited: raw argmax  AND  deployed smoothing (T={temperature}).")

    df = pd.read_excel(args.annotations, sheet_name="Frame_Annotations")
    df = df.dropna(subset=["Class"])
    df["Class"] = df["Class"].astype(str).str.strip()
    chips = args.chips or sorted(df["Chip_ID"].astype(str).unique())

    per_class = ui.CLASS_LABELS
    conf_mats = {}          # chip -> confusion (human x model) on argmax
    conf_rows = []
    trap_rows = []
    disagreements = []

    for chip in chips:
        sub = df[df["Chip_ID"].astype(str) == chip]
        if args.position:
            sub = sub[sub["Position"].astype(str).str.lower() == args.position.lower()]
        trap_keys = sorted({(str(r["Position"]), int(r["Trap_ID"])) for _, r in sub.iterrows()})
        if chip != "JM135_SixCondition_33" and args.max_old_traps is not None:
            trap_keys = trap_keys[: args.max_old_traps]
        if not trap_keys:
            continue
        cm = np.zeros((len(per_class), len(per_class)), dtype=np.int64)
        conf_by_true = {c: [] for c in per_class}
        print(f"\n--- {chip}: auditing {len(trap_keys)} traps ---")

        for position, trap_id in trap_keys:
            fpath = find_trap_file(chip, position, trap_id)
            if fpath is None:
                print(f"    [skip] no TIFF for {chip}/{position}/trap {trap_id}")
                continue
            with tif.TiffFile(fpath) as tf_file:
                stack = [p.asarray() for p in tf_file.pages]

            g = sub[(sub["Position"].astype(str) == position) & (sub["Trap_ID"] == trap_id)]
            g = g.sort_values("Frame")
            human = {int(r["Frame"]): str(r["Class"]) for _, r in g.iterrows()}
            coords = {int(r["Frame"]): coords_from_row(r) for _, r in g.iterrows()}

            probs, am_labels, sm_labels = run_trap(model, stack, coords, transitions, temperature)

            # ---- frame-level confusion (argmax vs. human, biological classes only)
            for f_i, h_lbl in human.items():
                if h_lbl in EXCLUDED_FROM_CONFUSION or h_lbl not in per_class:
                    continue
                if f_i >= len(am_labels):
                    continue
                m_lbl = am_labels[f_i]
                cm[per_class.index(h_lbl), per_class.index(m_lbl)] += 1
                conf_by_true[h_lbl].append(float(probs[f_i].max()))
                if m_lbl != h_lbl:
                    disagreements.append({
                        "Chip_ID": chip, "Position": position, "Trap_ID": trap_id,
                        "Frame": f_i, "Human": h_lbl, "Model_argmax": m_lbl,
                        "Model_conf": float(probs[f_i].max()),
                        "Smoothed": sm_labels[f_i] if sm_labels else "",
                    })

            # ---- event / RLS audit (pre-escape prefix, like the human RLS)
            frames_sorted = sorted(human)
            hseq = [human[f_] for f_ in frames_sorted]
            if "Mother Escaped (Ignore Rest)" in hseq:
                cut = hseq.index("Mother Escaped (Ignore Rest)")
                frames_sorted, hseq = frames_sorted[:cut], hseq[:cut]
            if not hseq:
                continue
            h_rls = ui.calculate_trap_rls(hseq)
            h_ev = ui.find_division_frames(hseq)

            end = frames_sorted[-1] + 1 if frames_sorted else len(am_labels)
            row = {"Chip_ID": chip, "Position": position, "Trap_ID": trap_id,
                   "n_frames": len(hseq), "human_RLS": h_rls["rls_count"],
                   "human_died": h_rls["died_on_chip"]}
            for name, labels in (("argmax", am_labels[:end]),
                                 ("smoothed", sm_labels[:end] if sm_labels else None)):
                if labels is None:
                    row[f"{name}_RLS"] = ""
                    continue
                m_rls = ui.calculate_trap_rls(labels)
                m_ev = ui.find_division_frames(labels)
                matched, missed, spurious = match_events(h_ev, m_ev)
                row[f"{name}_RLS"] = m_rls["rls_count"]
                row[f"{name}_signed_err"] = m_rls["rls_count"] - h_rls["rls_count"]
                row[f"{name}_died"] = m_rls["died_on_chip"]
                row[f"{name}_ev_matched"] = matched
                row[f"{name}_ev_missed"] = missed
                row[f"{name}_ev_spurious"] = spurious
            trap_rows.append(row)
            print(f"    {position}/trap {trap_id:>3}: human RLS={h_rls['rls_count']:>3} | "
                  f"argmax RLS={row.get('argmax_RLS')} | smoothed RLS={row.get('smoothed_RLS')}")

        conf_mats[chip] = cm
        # per-chip frame summary
        tot = cm.sum()
        if tot:
            print(f"\n  {chip} frame accuracy (argmax): {np.trace(cm)/tot*100:.1f}%  "
                  f"on {tot} labeled frames")
            for i, c in enumerate(per_class):
                row_sum = cm[i].sum()
                if row_sum == 0:
                    continue
                rec = cm[i, i] / row_sum
                to_mother = cm[i, per_class.index("Mother")] / row_sum
                mc = np.mean(conf_by_true[c]) if conf_by_true[c] else float("nan")
                print(f"    {c:<24s} recall={rec*100:5.1f}%  ->Mother={to_mother*100:5.1f}%  "
                      f"n={row_sum:<6d} mean maxP={mc*100:4.1f}%")
            conf_rows.append(pd.DataFrame(cm, index=[f"human:{c}" for c in per_class],
                                          columns=[f"model:{c}" for c in per_class]
                                          ).assign(Chip_ID=chip))

    # ---------------------------------------------------------------- outputs
    if conf_rows:
        pd.concat(conf_rows).to_csv(os.path.join(OUT_DIR, "confusion_matrices.csv"))
    tr = pd.DataFrame(trap_rows)
    if not tr.empty:
        tr.to_csv(os.path.join(OUT_DIR, "per_trap_rls.csv"), index=False)
        print("\n" + "=" * 78)
        print("TRAP-LEVEL RLS SUMMARY (the HEARTH gate numbers)")
        print("=" * 78)
        for chip, g in tr.groupby("Chip_ID"):
            for mode in ("argmax", "smoothed"):
                col = f"{mode}_signed_err"
                if col not in g or g[col].eq("").all():
                    continue
                e = pd.to_numeric(g[col], errors="coerce").dropna()
                if e.empty:
                    continue
                print(f"  {chip:<32s} [{mode:8s}] MAE={e.abs().mean():6.2f}  "
                      f"bias={e.mean():+6.2f}  exact={(e == 0).mean()*100:4.0f}%  "
                      f"within+/-1={(e.abs() <= 1).mean()*100:4.0f}%  n={len(e)}")
    dg = pd.DataFrame(disagreements)
    if not dg.empty:
        dg = dg.sort_values("Model_conf", ascending=False)
        dg.head(300).to_csv(os.path.join(OUT_DIR, "frame_disagreements.csv"), index=False)
        print(f"\nTop disagreements written to {OUT_DIR}/frame_disagreements.csv "
              f"({len(dg)} disagreeing frames total) -- open the worst ones in the UI.")

    if problems:
        print("\nFIX ORDER SUGGESTED BY THIS AUDIT:")
        print("  1. Retrain with the current train_classifier.py INCLUDING the "
              "JM135_SixCondition_33 annotations (the deployed model has never seen "
              "this chip).")
        print("  2. If the deployment gate fails again, the candidate_* metrics tell you "
              "whether the division-event head is usable even while the state head is not.")
        print("  3. Until then, treat the UI's 'Classifier Counted Trap RLS' as "
              "decorative -- it reflects the stale state model, not the calibrated "
              "division detector.")


if __name__ == "__main__":
    main()
