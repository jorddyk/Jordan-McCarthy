"""
train_rls_sequence_refiner.py -- sequence-level RLS count refiner for the
2026-08-14 direct-event candidate.

WHY THIS EXISTS
---------------
The direct framewise event detector cut held-out RLS MAE from 5.22 to 2.44
and solved death calling (93.8%), but it still decides each division from a
3-frame local view and then counts thresholded peaks.  That is now the
bottleneck.

This script DOES NOT retrain the expensive image models.  It consumes the
candidate artifacts already produced by train_classifier.py and learns a
trap-level temporal convolutional network (TCN) over their probability
sequences.  The key change is a differentiable COUNT objective: the model's
RLS prediction is the masked sum of per-frame division probability mass, so
training directly penalizes "one extra/missed division" at the trap endpoint.

Inputs expected in the working directory:
  train_classifier.py
  candidate_aging_chip_classifier.keras
  candidate_aging_chip_rls_detector.keras
  candidate_class_labels.json
  annotation/master_human_annotations.xlsx  (or AGING_ANNOTATION_PATH)
  extracted trap TIFFs                         (AGING_TRAPS_DIR)

Outputs:
  candidate_aging_chip_rls_refiner.keras
  candidate_rls_refiner_meta.json
  rls_refiner_test_concordance.csv

If the untouched test gate passes, the same artifacts are also written under
production names:
  aging_chip_rls_refiner.keras
  rls_refiner_meta.json

The test split is reconstructed with exactly the same seed/stratification as
the direct trainer.  It remains untouched until the final report.
"""

import os
import sys
import json
import math
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import LabelEncoder

import train_classifier as tc

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
STATE_MODEL = os.environ.get("AGING_CANDIDATE_STATE_MODEL", "candidate_aging_chip_classifier.keras")
RLS_MODEL = os.environ.get("AGING_CANDIDATE_RLS_MODEL", "candidate_aging_chip_rls_detector.keras")
CLASS_LABELS = os.environ.get("AGING_CANDIDATE_CLASS_LABELS", "candidate_class_labels.json")

REFINER_CANDIDATE_OUT = "candidate_aging_chip_rls_refiner.keras"
REFINER_PROD_OUT = "aging_chip_rls_refiner.keras"
META_CANDIDATE_OUT = "candidate_rls_refiner_meta.json"
META_PROD_OUT = "rls_refiner_meta.json"
TEST_REPORT_OUT = "rls_refiner_test_concordance.csv"

RANDOM_SEED = tc.RANDOM_SEED
BATCH_SIZE = 8
EPOCHS = 120
LR = 3e-4
EARLY_PATIENCE = 14
MIN_TRAP_FRAMES = 20  # exclude only obviously unfinished annotation fragments

TCN_WIDTH = 80
TCN_DILATIONS = (1, 2, 4, 8, 16)
TCN_DROPOUT = 0.12
EVENT_POS_WEIGHT = 6.0
DEAD_POS_WEIGHT = 2.0
LOSS_W_EVENT = 1.0
LOSS_W_DEAD = 0.20
LOSS_W_COUNT = 3.5

# Count calibration is intentionally low-capacity: an affine correction and an
# optional blend with the refiner's peak count.  This cannot memorize trap IDs.
COUNT_SCALES = np.round(np.arange(0.75, 1.251, 0.01), 2)
COUNT_OFFSETS = np.round(np.arange(-3.0, 3.01, 0.10), 2)
BLEND_WEIGHTS = np.round(np.arange(0.0, 1.01, 0.10), 2)  # weight on mass-count
DIV_THRESHOLDS = np.round(np.arange(0.10, 0.91, 0.05), 2).tolist()
DIV_MIN_GAPS = list(range(3, 13))

MAX_DEPLOY_TEST_MAE = tc.MAX_DEPLOY_TEST_MAE
MIN_DEPLOY_WITHIN1 = tc.MIN_DEPLOY_WITHIN1
MIN_DEPLOY_DEATH_AGREEMENT = tc.MIN_DEPLOY_DEATH_AGREEMENT


# ------------------------------------------------------------------------------
# Data preparation -- intentionally mirrors train_classifier.py
# ------------------------------------------------------------------------------
def load_filtered_annotations():
    if not os.path.exists(tc.ANNOTATION_PATH):
        raise FileNotFoundError(f"Annotation file not found: {tc.ANNOTATION_PATH}")

    df = pd.read_excel(tc.ANNOTATION_PATH, sheet_name="Frame_Annotations")
    df = df.dropna(subset=["Class"]).copy()
    df["Class"] = df["Class"].astype(str).str.strip()
    df = df[df["Class"].str.lower() != "nan"].reset_index(drop=True)

    escaped = {}
    for _, row in df[df["Class"].isin(["Mother Escaped (Ignore Rest)", "Mother Escaped"])].iterrows():
        key = (str(row["Position"]).strip().lower(), int(row["Trap_ID"]))
        escaped[key] = min(escaped.get(key, 10**9), int(row["Frame"]))

    def valid_pre_escape(row):
        key = (str(row["Position"]).strip().lower(), int(row["Trap_ID"]))
        return not (key in escaped and int(row["Frame"]) >= escaped[key])

    df = df[df.apply(valid_pre_escape, axis=1)].reset_index(drop=True)
    df = tc.phantom_guard(df)
    df = df[~df["Class"].isin(tc.EXCLUDE_CLASSES)].reset_index(drop=True)

    le = LabelEncoder()
    df["label_idx"] = le.fit_transform(df["Class"])
    return df, list(le.classes_)


def gpu_safe_predict(model, X, batch_size=tc.BATCH_SIZE):
    ds = tf.data.Dataset.from_tensor_slices(X).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return model.predict(ds, verbose=0)


def base_probability_features(X, class_names):
    print(f"--> Loading existing candidate state model: {STATE_MODEL}")
    state_model = tf.keras.models.load_model(STATE_MODEL, compile=False)
    print(f"--> Loading existing candidate direct-RLS model: {RLS_MODEL}")
    rls_model = tf.keras.models.load_model(RLS_MODEL, compile=False)

    state_logits = gpu_safe_predict(state_model, X)
    rls_out = gpu_safe_predict(rls_model, X)
    if not isinstance(rls_out, (list, tuple)) or len(rls_out) != 2:
        raise RuntimeError("candidate RLS model must return [division_logit, dead_logit]")
    div_logits, dead_logits = rls_out

    state_prob = tf.nn.softmax(state_logits, axis=-1).numpy().astype(np.float32)
    div_prob = tf.nn.sigmoid(np.asarray(div_logits)).numpy().reshape(-1).astype(np.float32)
    dead_prob = tf.nn.sigmoid(np.asarray(dead_logits)).numpy().reshape(-1).astype(np.float32)

    # Per-frame uncertainty is useful to the sequence model: high entropy often
    # marks precisely the Mother/Early/Late boundary that broke the old model.
    entropy = -np.sum(state_prob * np.log(state_prob + 1e-7), axis=1).astype(np.float32)

    # Semantic indices by name; missing classes simply contribute zeros.
    idx = {c: i for i, c in enumerate(class_names)}
    def col(name):
        return state_prob[:, idx[name]] if name in idx else np.zeros(len(state_prob), np.float32)

    mother = col("Mother")
    early = col("Early Bud")
    late = col("Late Bud")
    no_cell = col("No Cell")
    blurry = col("Out of Focus / Blurry")

    base = np.column_stack([
        state_prob,
        div_prob,
        dead_prob,
        entropy,
        mother + early,
        late,
        no_cell + blurry,
    ]).astype(np.float32)

    names = [f"state_p::{c}" for c in class_names] + [
        "base_division_p", "base_dead_p", "state_entropy",
        "mother_or_early_p", "late_p", "gap_p",
    ]
    return base, names


def exact_event_targets(meta_list, trap_orders):
    y = np.zeros(len(meta_list), dtype=np.float32)
    for key, order in trap_orders.items():
        labels = [meta_list[i]["class_str"] for i in order]
        for local_i in tc.find_division_frames(labels):
            y[order[local_i]] = 1.0
    return y


def eligible_keys(trap_orders):
    good = set()
    for key, order in trap_orders.items():
        if len(order) >= MIN_TRAP_FRAMES:
            good.add(key)
    return good


def make_sequence_arrays(base_features, feature_names, meta_list, trap_orders, human_rls,
                         y_event_exact, y_dead, keys, max_len):
    keys = sorted(keys)
    n = len(keys)
    fdim = base_features.shape[1] + 3  # time, transition proxy, base-div delta
    Xs = np.zeros((n, max_len, fdim), dtype=np.float32)
    masks = np.zeros((n, max_len, 1), dtype=np.float32)
    y_event = np.zeros((n, max_len, 1), dtype=np.float32)
    y_d = np.zeros((n, max_len, 1), dtype=np.float32)
    y_count = np.zeros((n, 1), dtype=np.float32)

    # Find semantic columns in the appended base feature names.
    late_col = feature_names.index("late_p")
    me_col = feature_names.index("mother_or_early_p")
    div_col = feature_names.index("base_division_p")

    for r, key in enumerate(keys):
        order = trap_orders[key]
        T = min(len(order), max_len)
        feat = base_features[order[:T]].copy()

        tnorm = np.linspace(0.0, 1.0, T, dtype=np.float32)
        late = feat[:, late_col]
        me = feat[:, me_col]
        trans_proxy = np.zeros(T, np.float32)
        if T > 1:
            trans_proxy[1:] = late[:-1] * me[1:]
        div_delta = np.zeros(T, np.float32)
        if T > 1:
            div_delta[1:] = feat[1:, div_col] - feat[:-1, div_col]

        full = np.column_stack([feat, tnorm, trans_proxy, div_delta]).astype(np.float32)
        Xs[r, :T] = full
        masks[r, :T, 0] = 1.0
        y_event[r, :T, 0] = y_event_exact[order[:T]]
        y_d[r, :T, 0] = y_dead[order[:T]]
        y_count[r, 0] = float(human_rls[key]["rls_count"])

    out_names = feature_names + ["time_norm", "late_to_motherearly_proxy", "base_division_delta"]
    return keys, Xs, masks, y_event, y_d, y_count, out_names


# ------------------------------------------------------------------------------
# Sequence model
# ------------------------------------------------------------------------------
@tf.keras.utils.register_keras_serializable(package="AgingChip")
class MaskedEventCount(layers.Layer):
    """Differentiable RLS count = sum of division probability over valid frames."""
    def call(self, inputs):
        event_prob, mask = inputs
        event_prob = tf.cast(event_prob, tf.float32)
        mask = tf.cast(mask, tf.float32)
        return tf.reduce_sum(event_prob * mask, axis=1)


@tf.keras.utils.register_keras_serializable(package="AgingChip")
def weighted_event_bce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-6, 1.0 - 1e-6)
    return -(EVENT_POS_WEIGHT * y_true * tf.math.log(y_pred) +
             (1.0 - y_true) * tf.math.log(1.0 - y_pred))


@tf.keras.utils.register_keras_serializable(package="AgingChip")
def weighted_dead_bce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-6, 1.0 - 1e-6)
    return -(DEAD_POS_WEIGHT * y_true * tf.math.log(y_pred) +
             (1.0 - y_true) * tf.math.log(1.0 - y_pred))


def build_refiner(max_len, n_features, event_rate):
    feat_in = layers.Input((max_len, n_features), name="sequence_features")
    mask_in = layers.Input((max_len, 1), name="valid_mask")

    x = layers.LayerNormalization(name="seq_norm")(feat_in)
    x = layers.Multiply(name="mask_input")([x, mask_in])
    x = layers.Conv1D(TCN_WIDTH, 1, padding="same", activation="swish", name="seq_project")(x)

    for d in TCN_DILATIONS:
        residual = x
        y = layers.Conv1D(TCN_WIDTH, 5, padding="same", dilation_rate=d,
                          activation="swish", name=f"tcn_d{d}_c1")(x)
        y = layers.Dropout(TCN_DROPOUT, name=f"tcn_d{d}_drop")(y)
        y = layers.Conv1D(TCN_WIDTH, 3, padding="same", dilation_rate=d,
                          activation=None, name=f"tcn_d{d}_c2")(y)
        x = layers.Add(name=f"tcn_d{d}_add")([residual, y])
        x = layers.Activation("swish", name=f"tcn_d{d}_act")(x)
        x = layers.Multiply(name=f"tcn_d{d}_mask")([x, mask_in])

    # Initialize event prior near the empirical training event prevalence so the
    # initial summed count is biologically plausible instead of ~T/2.
    event_rate = float(np.clip(event_rate, 1e-4, 1.0 - 1e-4))
    event_bias = math.log(event_rate / (1.0 - event_rate))
    event_prob = layers.Dense(
        1, activation="sigmoid", dtype="float32",
        bias_initializer=tf.keras.initializers.Constant(event_bias),
        name="event_prob"
    )(x)
    dead_prob = layers.Dense(1, activation="sigmoid", dtype="float32", name="dead_prob")(x)
    count = MaskedEventCount(name="rls_count")([event_prob, mask_in])

    model = models.Model([feat_in, mask_in],
                         {"event_prob": event_prob, "dead_prob": dead_prob, "rls_count": count},
                         name="aging_chip_rls_sequence_refiner")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR),
        loss={
            "event_prob": weighted_event_bce,
            "dead_prob": weighted_dead_bce,
            "rls_count": tf.keras.losses.Huber(delta=1.0),
        },
        loss_weights={
            "event_prob": LOSS_W_EVENT,
            "dead_prob": LOSS_W_DEAD,
            "rls_count": LOSS_W_COUNT,
        },
        metrics={"rls_count": [tf.keras.metrics.MeanAbsoluteError(name="mae")]},
    )
    return model


def fit_refiner(model, tr, ca):
    tr_keys, Xtr, Mtr, Etr, Dtr, Ctr, _ = tr
    ca_keys, Xca, Mca, Eca, Dca, Cca, _ = ca
    sw_tr = {
        "event_prob": Mtr[:, :, 0],
        "dead_prob": Mtr[:, :, 0],
        "rls_count": np.ones(len(tr_keys), dtype=np.float32),
    }
    sw_ca = {
        "event_prob": Mca[:, :, 0],
        "dead_prob": Mca[:, :, 0],
        "rls_count": np.ones(len(ca_keys), dtype=np.float32),
    }

    print("\n================ STAGE 3: sequence-level count-constrained TCN ================")
    model.fit(
        {"sequence_features": Xtr, "valid_mask": Mtr},
        {"event_prob": Etr, "dead_prob": Dtr, "rls_count": Ctr},
        sample_weight=sw_tr,
        validation_data=(
            {"sequence_features": Xca, "valid_mask": Mca},
            {"event_prob": Eca, "dead_prob": Dca, "rls_count": Cca},
            sw_ca,
        ),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[
            EarlyStopping(monitor="val_rls_count_mae", mode="min", patience=EARLY_PATIENCE,
                          restore_best_weights=True),
            ReduceLROnPlateau(monitor="val_rls_count_mae", mode="min", factor=0.5,
                              patience=5, min_lr=1e-6),
        ],
        verbose=1 if sys.stdout.isatty() else 2,
    )


def predict_refiner(model, arr):
    keys, Xs, Ms, Ev, Dd, Cc, names = arr
    out = model.predict({"sequence_features": Xs, "valid_mask": Ms}, batch_size=BATCH_SIZE, verbose=0)
    event = np.asarray(out["event_prob"], dtype=np.float64)[:, :, 0]
    dead = np.asarray(out["dead_prob"], dtype=np.float64)[:, :, 0]
    count = np.asarray(out["rls_count"], dtype=np.float64).reshape(-1)
    lengths = Ms[:, :, 0].sum(axis=1).astype(int)
    return keys, event, dead, count, lengths


# ------------------------------------------------------------------------------
# Endpoint calibration / evaluation
# ------------------------------------------------------------------------------
def peak_counts(event, lengths, threshold, min_gap):
    return np.asarray([
        len(tc.pick_division_events(event[i, :lengths[i]], threshold, min_gap))
        for i in range(len(lengths))
    ], dtype=np.float64)


def calibrate_peak_decoder(keys, event, lengths, human_rls):
    best = None
    y = np.asarray([human_rls[k]["rls_count"] for k in keys], dtype=np.float64)
    for thr in DIV_THRESHOLDS:
        for gap in DIV_MIN_GAPS:
            p = peak_counts(event, lengths, thr, gap)
            err = np.abs(p - y)
            rank = (err.mean(), -(err <= 1).mean(), -(err == 0).mean(), abs((p-y).mean()))
            if best is None or rank < best[0]:
                best = (rank, {"threshold": float(thr), "min_gap": int(gap)}, p)
    return best[1], best[2]


def calibrate_count_combiner(keys, mass_count, peak_count, human_rls):
    y = np.asarray([human_rls[k]["rls_count"] for k in keys], dtype=np.float64)
    best = None
    # First find a low-capacity affine calibration for the differentiable mass count.
    for a in COUNT_SCALES:
        for b in COUNT_OFFSETS:
            mass_adj = np.maximum(0.0, a * mass_count + b)
            for w in BLEND_WEIGHTS:
                cont = w * mass_adj + (1.0 - w) * peak_count
                pred = np.rint(cont)
                err = np.abs(pred - y)
                bias = (pred - y).mean()
                rank = (err.mean(), -(err <= 1).mean(), -(err == 0).mean(), abs(bias), abs(a-1.0), abs(b))
                if best is None or rank < best[0]:
                    best = (rank, {
                        "mass_scale": float(a),
                        "mass_offset": float(b),
                        "mass_blend_weight": float(w),
                    })
    return best[1]


def apply_count_combiner(mass_count, peak_count, cfg):
    mass_adj = np.maximum(0.0, cfg["mass_scale"] * mass_count + cfg["mass_offset"])
    cont = cfg["mass_blend_weight"] * mass_adj + (1.0 - cfg["mass_blend_weight"]) * peak_count
    return np.maximum(0.0, np.rint(cont)).astype(int)


def calibrate_death(keys, dead, lengths, human_rls):
    by = {k: dead[i, :lengths[i]] for i, k in enumerate(keys)}
    return tc.calibrate_death_decoder(by, human_rls)


def evaluate(keys, event, dead, mass_count, lengths, human_rls, peak_cfg, count_cfg, death_cfg):
    peaks = peak_counts(event, lengths, peak_cfg["threshold"], peak_cfg["min_gap"])
    pred_rls = apply_count_combiner(mass_count, peaks, count_cfg)
    rows = []
    for i, k in enumerate(keys):
        true_rls = int(human_rls[k]["rls_count"])
        pred_dead, pred_death_frame = tc.sustained_death(
            dead[i, :lengths[i]], death_cfg["threshold"], death_cfg["persistence"]
        )
        true_dead = bool(human_rls[k]["died_on_chip"])
        rows.append({
            "chip": k[0], "position": k[1], "trap_id": k[2],
            "true_rls": true_rls, "pred_rls": int(pred_rls[i]),
            "signed_error": int(pred_rls[i] - true_rls),
            "abs_error": int(abs(pred_rls[i] - true_rls)),
            "mass_count_raw": float(mass_count[i]),
            "peak_count": int(peaks[i]),
            "true_died": true_dead, "pred_died": bool(pred_dead),
            "pred_death_frame": pred_death_frame,
        })
    report = pd.DataFrame(rows)
    metrics = {
        "mae": float(report["abs_error"].mean()),
        "bias": float(report["signed_error"].mean()),
        "exact": float((report["abs_error"] == 0).mean()),
        "within1": float((report["abs_error"] <= 1).mean()),
        "death_agreement": float((report["true_died"] == report["pred_died"]).mean()),
        "n_traps": int(len(report)),
    }
    return report, metrics


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(RANDOM_SEED)
    tf.random.set_seed(RANDOM_SEED)

    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for g in gpus:
            try:
                tf.config.experimental.set_memory_growth(g, True)
            except Exception:
                pass
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
        print(f"--> {len(gpus)} GPU(s) detected: mixed_float16 enabled.")

    for p in (STATE_MODEL, RLS_MODEL, CLASS_LABELS):
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required candidate artifact not found: {p}")

    df, encoded_names = load_filtered_annotations()
    candidate_names = json.load(open(CLASS_LABELS))
    if list(encoded_names) != list(candidate_names):
        raise RuntimeError(
            "Class ordering/database mismatch between candidate model and current annotations. "
            f"candidate={candidate_names} current={encoded_names}. Use the same frozen annotation copy "
            "that produced the candidate run."
        )

    fmap = tc.map_trap_files(tc.TRAPS_DIR)
    X, y_state, meta_list = tc.load_frames(df, fmap)
    trap_orders = tc.build_trap_orders(meta_list)
    y_div_soft, y_dead, human_rls = tc.build_endpoint_targets(meta_list, trap_orders)
    y_event_exact = exact_event_targets(meta_list, trap_orders)

    good = eligible_keys(trap_orders)
    # Reconstruct the original split FIRST, then drop only obvious incomplete fragments.
    tr_all, ca_all, te_all = tc.stratified_trap_split(trap_orders)
    train_keys = tr_all & good
    cal_keys = ca_all & good
    test_keys = te_all & good
    if len(cal_keys) < 5 or len(test_keys) < 5:
        raise RuntimeError("Too few eligible calibration/test traps after fragment filtering.")

    print(f"--> Sequence split: {len(train_keys)} train / {len(cal_keys)} calibration / "
          f"{len(test_keys)} untouched test (MIN_TRAP_FRAMES={MIN_TRAP_FRAMES})")

    base_feat, base_names = base_probability_features(X, candidate_names)
    max_len = max(len(trap_orders[k]) for k in good)

    tr = make_sequence_arrays(base_feat, base_names, meta_list, trap_orders, human_rls,
                              y_event_exact, y_dead, train_keys, max_len)
    ca = make_sequence_arrays(base_feat, base_names, meta_list, trap_orders, human_rls,
                              y_event_exact, y_dead, cal_keys, max_len)
    te = make_sequence_arrays(base_feat, base_names, meta_list, trap_orders, human_rls,
                              y_event_exact, y_dead, test_keys, max_len)

    event_rate = float(np.sum(tr[3] * tr[2]) / np.sum(tr[2]))
    print(f"--> Exact event prevalence in sequence training frames: {event_rate*100:.2f}%")
    print(f"--> Sequence tensor: max_len={max_len}, features={tr[1].shape[-1]}")

    refiner = build_refiner(max_len, tr[1].shape[-1], event_rate)
    fit_refiner(refiner, tr, ca)

    # Calibration split: choose peak decoder, then a very-low-capacity combination
    # of differentiable mass count and peak count, plus death persistence.
    ca_keys, ca_event, ca_dead, ca_mass, ca_len = predict_refiner(refiner, ca)
    peak_cfg, ca_peaks = calibrate_peak_decoder(ca_keys, ca_event, ca_len, human_rls)
    count_cfg = calibrate_count_combiner(ca_keys, ca_mass, ca_peaks, human_rls)
    death_cfg = calibrate_death(ca_keys, ca_dead, ca_len, human_rls)
    _, cal_metrics = evaluate(ca_keys, ca_event, ca_dead, ca_mass, ca_len, human_rls,
                              peak_cfg, count_cfg, death_cfg)

    print("\n================ CALIBRATION ENDPOINT ================")
    print(f"RLS MAE:               {cal_metrics['mae']:.2f}")
    print(f"Within +/-1 division:  {cal_metrics['within1']*100:.1f}%")
    print(f"Death-call agreement:  {cal_metrics['death_agreement']*100:.1f}%")
    print(f"Peak decoder:          thr={peak_cfg['threshold']:.2f}, gap={peak_cfg['min_gap']}")
    print(f"Count combiner:        scale={count_cfg['mass_scale']:.2f}, "
          f"offset={count_cfg['mass_offset']:+.2f}, mass_weight={count_cfg['mass_blend_weight']:.1f}")

    # Untouched test -- first and only use of these trap targets for model assessment.
    te_keys, te_event, te_dead, te_mass, te_len = predict_refiner(refiner, te)
    test_report, test_metrics = evaluate(te_keys, te_event, te_dead, te_mass, te_len, human_rls,
                                         peak_cfg, count_cfg, death_cfg)
    test_report.to_csv(TEST_REPORT_OUT, index=False)

    print("\n================ UNTOUCHED TEST REPORT: SEQUENCE REFINER ================")
    print(f"Test traps:            {test_metrics['n_traps']}")
    print(f"RLS MAE:               {test_metrics['mae']:.2f} divisions")
    print(f"RLS bias:              {test_metrics['bias']:+.2f} divisions")
    print(f"Exact RLS match:       {test_metrics['exact']*100:.1f}%")
    print(f"Within +/-1 division:  {test_metrics['within1']*100:.1f}%")
    print(f"Death-call agreement:  {test_metrics['death_agreement']*100:.1f}%")

    deployment_ok = (
        test_metrics["mae"] <= MAX_DEPLOY_TEST_MAE
        and test_metrics["within1"] >= MIN_DEPLOY_WITHIN1
        and test_metrics["death_agreement"] >= MIN_DEPLOY_DEATH_AGREEMENT
    )

    meta = {
        "method": "TCN sequence refiner with differentiable trap-level event-mass count",
        "base_state_model": STATE_MODEL,
        "base_rls_model": RLS_MODEL,
        "feature_names": tr[6],
        "max_sequence_length": int(max_len),
        "min_trap_frames": MIN_TRAP_FRAMES,
        "peak_decoder": peak_cfg,
        "count_combiner": count_cfg,
        "death_decoder": death_cfg,
        "calibration_metrics": cal_metrics,
        "test_metrics": test_metrics,
        "deployment_gate": {
            "max_test_mae": MAX_DEPLOY_TEST_MAE,
            "min_within1": MIN_DEPLOY_WITHIN1,
            "min_death_agreement": MIN_DEPLOY_DEATH_AGREEMENT,
        },
        "deployment_ok": bool(deployment_ok),
    }

    # Always preserve the candidate/refiner evidence.
    refiner.save(REFINER_CANDIDATE_OUT)
    with open(META_CANDIDATE_OUT, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDEPLOYMENT GATE: {'PASS' if deployment_ok else 'FAIL'} | "
          f"requires MAE<={MAX_DEPLOY_TEST_MAE:.2f}, "
          f"within1>={MIN_DEPLOY_WITHIN1*100:.0f}%, "
          f"death>={MIN_DEPLOY_DEATH_AGREEMENT*100:.0f}%")
    print(f"--> Refiner test concordance: {TEST_REPORT_OUT}")
    print(f"--> Saved candidate refiner:  {REFINER_CANDIDATE_OUT}")

    if deployment_ok:
        refiner.save(REFINER_PROD_OUT)
        with open(META_PROD_OUT, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"--> PRODUCTION refiner written: {REFINER_PROD_OUT}")
        print("\nDONE: sequence-level RLS endpoint gate PASSED.")
    else:
        print("\nRefiner did not clear the production endpoint gate; production artifacts were not overwritten.")
        sys.exit(2)
