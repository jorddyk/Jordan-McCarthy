"""
train_temporal_residual_rls.py

Long-context residual corrector for the 2026-08-14 direct RLS detector.

WHY THIS VERSION
----------------
The direct image model reached held-out RLS MAE 2.44 with good death calling,
while the first sequence refiner got worse (2.62).  The refiner's mistake was
throwing away the image model's rich latent representation and then forcing a
sparse event sequence to satisfy a global probability-mass count loss.

This trainer keeps the strongest thing we already have -- the direct detector
-- and learns ONLY a temporal correction to its division logit.  It uses the
frozen image encoder's 256-D fusion embedding plus state/death probabilities
across each full trap.  The correction head is zero-initialized, so epoch 0 is
exactly the existing direct detector.  A new model is accepted only when its
CALIBRATION-trap RLS endpoint improves over that baseline.  The untouched test
traps are evaluated once at the end.

No HMM.  No differentiable count-mass surrogate.  No thresholded refiner
probability blend.  RLS is still the biologically defined count of discrete
completed-division events, with threshold/min-gap chosen only on calibration
traps.

Required in the Euler working directory:
  train_classifier.py
  candidate_aging_chip_classifier.keras
  candidate_aging_chip_rls_detector.keras
  candidate_class_labels.json
  annotation/master_human_annotations.xlsx (or AGING_ANNOTATION_PATH)
  extracted trap TIFFs                (or AGING_TRAPS_DIR)

Outputs:
  candidate_aging_chip_temporal_rls_corrector.keras
  candidate_temporal_rls_meta.json
  rls_temporal_test_concordance.csv

Production artifacts are written only if the same hard test gate from
train_classifier.py is passed.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.callbacks import ReduceLROnPlateau

import train_classifier as tc

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
STATE_MODEL = os.environ.get("AGING_CANDIDATE_STATE_MODEL", "candidate_aging_chip_classifier.keras")
RLS_MODEL = os.environ.get("AGING_CANDIDATE_RLS_MODEL", "candidate_aging_chip_rls_detector.keras")
CLASS_LABELS = os.environ.get("AGING_CANDIDATE_CLASS_LABELS", "candidate_class_labels.json")

CANDIDATE_MODEL_OUT = "candidate_aging_chip_temporal_rls_corrector.keras"
CANDIDATE_META_OUT = "candidate_temporal_rls_meta.json"
PRODUCTION_MODEL_OUT = "aging_chip_temporal_rls_corrector.keras"
PRODUCTION_META_OUT = "temporal_rls_meta.json"
TEST_REPORT_OUT = "rls_temporal_test_concordance.csv"
CHECKPOINT = "temporal_rls_best.weights.h5"

RANDOM_SEED = tc.RANDOM_SEED
BATCH_SIZE = 6
EPOCHS = 70
LR = 3e-4
ENDPOINT_PATIENCE = 12
MIN_EPOCHS = 8

TCN_WIDTH = 96
TCN_DILATIONS = (1, 2, 4, 8)
TCN_DROPOUT = 0.15
L2 = 1e-4

# Positive events are sparse.  This is a SAMPLE weight, not a different target
# definition.  The decoder threshold is independently calibrated afterward.
EXACT_EVENT_WEIGHT = 10.0
SOFT_NEIGHBOR_WEIGHT = 3.0
HARD_NEGATIVE_WEIGHT = 1.75
HARD_NEGATIVE_BASE_P = 0.10

MAX_DEPLOY_TEST_MAE = tc.MAX_DEPLOY_TEST_MAE
MIN_DEPLOY_WITHIN1 = tc.MIN_DEPLOY_WITHIN1
MIN_DEPLOY_DEATH_AGREEMENT = tc.MIN_DEPLOY_DEATH_AGREEMENT


# -----------------------------------------------------------------------------
# Annotation + image-feature preparation
# -----------------------------------------------------------------------------
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

    def before_escape(row):
        key = (str(row["Position"]).strip().lower(), int(row["Trap_ID"]))
        return not (key in escaped and int(row["Frame"]) >= escaped[key])

    df = df[df.apply(before_escape, axis=1)].reset_index(drop=True)
    df = tc.phantom_guard(df)
    df = df[~df["Class"].isin(tc.EXCLUDE_CLASSES)].reset_index(drop=True)

    # Match the candidate classifier class order exactly.
    candidate_names = json.load(open(CLASS_LABELS))
    lut = {c: i for i, c in enumerate(candidate_names)}
    unknown = sorted(set(df["Class"]) - set(lut))
    if unknown:
        raise RuntimeError(f"Current annotation file contains classes absent from candidate model: {unknown}")
    df["label_idx"] = df["Class"].map(lut).astype(int)
    return df, candidate_names


def predict_batched(model, X, batch_size=tc.BATCH_SIZE):
    ds = tf.data.Dataset.from_tensor_slices(X).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return model.predict(ds, verbose=0)


def extract_base_features(X, class_names):
    print(f"--> Loading candidate state model: {STATE_MODEL}")
    state_model = tf.keras.models.load_model(STATE_MODEL, compile=False)
    print(f"--> Loading candidate direct-RLS model: {RLS_MODEL}")
    rls_model = tf.keras.models.load_model(RLS_MODEL, compile=False)

    try:
        fusion_layer = state_model.get_layer("fusion_dense")
    except Exception:
        available = [l.name for l in state_model.layers]
        raise RuntimeError(
            "The candidate state model does not expose layer 'fusion_dense'. "
            f"Available layers include: {available[-20:]}"
        )

    embed_model = models.Model(state_model.input, fusion_layer.output, name="frozen_fusion_embedding")

    print("--> Extracting frozen visual embeddings / base probabilities...")
    embedding = np.asarray(predict_batched(embed_model, X), dtype=np.float32)
    state_logits = np.asarray(predict_batched(state_model, X), dtype=np.float32)
    rls_out = predict_batched(rls_model, X)
    if not isinstance(rls_out, (list, tuple)) or len(rls_out) != 2:
        raise RuntimeError("candidate RLS model must return [division_logit, dead_logit]")

    div_logits = np.asarray(rls_out[0], dtype=np.float32).reshape(-1)
    dead_logits = np.asarray(rls_out[1], dtype=np.float32).reshape(-1)
    state_prob = tf.nn.softmax(state_logits, axis=-1).numpy().astype(np.float32)
    div_prob = tf.nn.sigmoid(div_logits).numpy().astype(np.float32)
    dead_prob = tf.nn.sigmoid(dead_logits).numpy().astype(np.float32)
    entropy = -np.sum(state_prob * np.log(state_prob + 1e-7), axis=1).astype(np.float32)

    idx = {c: i for i, c in enumerate(class_names)}
    def col(name):
        return state_prob[:, idx[name]] if name in idx else np.zeros(len(state_prob), np.float32)

    mother = col("Mother")
    early = col("Early Bud")
    late = col("Late Bud")
    gap = col("No Cell") + col("Out of Focus / Blurry")

    # The TCN sees rich morphology plus calibrated semantic summaries.  The raw
    # center division LOGIT is supplied separately as the residual baseline.
    feat = np.column_stack([
        embedding,
        state_prob,
        div_prob,
        dead_prob,
        entropy,
        mother + early,
        late,
        gap,
    ]).astype(np.float32)

    names = [f"fusion_{i}" for i in range(embedding.shape[1])]
    names += [f"state_p::{c}" for c in class_names]
    names += ["base_division_p", "base_dead_p", "state_entropy",
              "mother_or_early_p", "late_p", "gap_p"]
    return feat, names, div_logits.astype(np.float32), dead_prob


def normalize_features(feat, train_idx):
    mu = feat[train_idx].mean(axis=0).astype(np.float32)
    sd = feat[train_idx].std(axis=0).astype(np.float32)
    sd[sd < 1e-5] = 1.0
    return ((feat - mu) / sd).astype(np.float32), mu, sd


def make_sequence_arrays(feat, base_div_logits, y_div, meta_list, trap_orders, keys):
    keys = sorted(keys)
    max_len = max(len(trap_orders[k]) for k in trap_orders)
    n = len(keys)
    fdim = feat.shape[1] + 2  # + normalized time + base probability first-difference

    Xs = np.zeros((n, max_len, fdim), dtype=np.float32)
    Bs = np.zeros((n, max_len, 1), dtype=np.float32)
    Ys = np.zeros((n, max_len, 1), dtype=np.float32)
    Ms = np.zeros((n, max_len), dtype=np.float32)
    Ws = np.zeros((n, max_len), dtype=np.float32)
    lengths = np.zeros(n, dtype=np.int32)

    base_p = tf.nn.sigmoid(base_div_logits).numpy().astype(np.float32)

    for r, key in enumerate(keys):
        order = trap_orders[key]
        T = len(order)
        lengths[r] = T
        f = feat[order].copy()
        tnorm = np.linspace(0.0, 1.0, T, dtype=np.float32)
        delta = np.zeros(T, dtype=np.float32)
        if T > 1:
            delta[1:] = base_p[order[1:]] - base_p[order[:-1]]
        full = np.column_stack([f, tnorm, delta]).astype(np.float32)

        Xs[r, :T] = full
        Bs[r, :T, 0] = base_div_logits[order]
        Ys[r, :T, 0] = y_div[order]
        Ms[r, :T] = 1.0

        # Sample weights: exact events > soft +/-1 neighbors > hard negatives > background.
        w = np.ones(T, dtype=np.float32)
        tgt = y_div[order]
        w[tgt >= 0.99] = EXACT_EVENT_WEIGHT
        soft = (tgt > 0.0) & (tgt < 0.99)
        w[soft] = SOFT_NEIGHBOR_WEIGHT
        hard_neg = (tgt <= 0.0) & (base_p[order] >= HARD_NEGATIVE_BASE_P)
        w[hard_neg] = HARD_NEGATIVE_WEIGHT
        Ws[r, :T] = w

    return keys, Xs, Bs, Ys, Ms, Ws, lengths


def flat_prob_by_trap(flat_values, trap_orders, keys):
    out = {}
    for k in keys:
        out[k] = np.asarray(flat_values[trap_orders[k]], dtype=np.float64)
    return out


# -----------------------------------------------------------------------------
# Temporal residual model
# -----------------------------------------------------------------------------
def build_temporal_corrector(max_len, n_features):
    feat_in = layers.Input((max_len, n_features), name="sequence_features")
    base_logit_in = layers.Input((max_len, 1), name="base_division_logit")

    x = layers.LayerNormalization(name="feature_norm")(feat_in)
    x = layers.Conv1D(
        TCN_WIDTH, 1, padding="same", activation="swish",
        kernel_regularizer=regularizers.l2(L2), name="project"
    )(x)

    for d in TCN_DILATIONS:
        residual = x
        y = layers.Conv1D(
            TCN_WIDTH, 3, padding="same", dilation_rate=d, activation="swish",
            kernel_regularizer=regularizers.l2(L2), name=f"tcn_d{d}_c1"
        )(x)
        y = layers.Dropout(TCN_DROPOUT, name=f"tcn_d{d}_drop")(y)
        y = layers.Conv1D(
            TCN_WIDTH, 3, padding="same", dilation_rate=d, activation=None,
            kernel_regularizer=regularizers.l2(L2), name=f"tcn_d{d}_c2"
        )(y)
        x = layers.Add(name=f"tcn_d{d}_add")([residual, y])
        x = layers.Activation("swish", name=f"tcn_d{d}_act")(x)

    # Zero init is critical: before learning, corrected_logit == base_logit.
    correction = layers.Dense(
        1,
        activation=None,
        dtype="float32",
        kernel_initializer="zeros",
        bias_initializer="zeros",
        kernel_regularizer=regularizers.l2(L2),
        name="temporal_logit_correction",
    )(x)
    corrected = layers.Add(name="corrected_division_logit")([base_logit_in, correction])

    model = models.Model(
        {"sequence_features": feat_in, "base_division_logit": base_logit_in},
        corrected,
        name="aging_chip_temporal_residual_rls",
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR),
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.AUC(name="auc", from_logits=True)],
    )
    return model


def sigmoid_np(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.clip(x, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x))


def model_prob_by_trap(model, arr):
    keys, Xs, Bs, Ys, Ms, Ws, lengths = arr
    logits = model.predict(
        {"sequence_features": Xs, "base_division_logit": Bs},
        batch_size=BATCH_SIZE,
        verbose=0,
    )[:, :, 0]
    probs = sigmoid_np(logits)
    return {k: probs[i, :lengths[i]] for i, k in enumerate(keys)}


def endpoint_rank(metrics):
    return (
        metrics["mae"],
        -metrics["within1"],
        -metrics["exact"],
        abs(metrics["bias"]),
    )


class EndpointCheckpoint(tf.keras.callbacks.Callback):
    def __init__(self, cal_arr, dead_by, human_rls, death_cfg, checkpoint_path,
                 baseline_rank, baseline_div_cfg, baseline_metrics):
        super().__init__()
        self.cal_arr = cal_arr
        self.dead_by = dead_by
        self.human_rls = human_rls
        self.death_cfg = death_cfg
        self.checkpoint_path = checkpoint_path
        self.best_rank = baseline_rank
        self.best_div_cfg = baseline_div_cfg
        self.best_metrics = baseline_metrics
        self.best_epoch = 0
        self.bad_epochs = 0

    def on_epoch_end(self, epoch, logs=None):
        div_by = model_prob_by_trap(self.model, self.cal_arr)
        div_cfg = tc.calibrate_division_decoder(div_by, self.human_rls)
        _, metrics = tc.evaluate_split(div_by, self.dead_by, self.human_rls, div_cfg, self.death_cfg)
        rank = endpoint_rank(metrics)

        print(
            f"\n[TEMPORAL endpoint] epoch {epoch+1}: "
            f"RLS_MAE={metrics['mae']:.2f} bias={metrics['bias']:+.2f} "
            f"exact={metrics['exact']*100:.1f}% within1={metrics['within1']*100:.1f}% | "
            f"thr={div_cfg['threshold']:.2f} gap={div_cfg['min_gap']}"
        )

        if rank < self.best_rank:
            self.best_rank = rank
            self.best_div_cfg = div_cfg
            self.best_metrics = metrics
            self.best_epoch = epoch + 1
            self.bad_epochs = 0
            self.model.save_weights(self.checkpoint_path)
            print(f"[TEMPORAL endpoint] NEW BEST -> saved {self.checkpoint_path}")
        else:
            self.bad_epochs += 1

        if epoch + 1 >= MIN_EPOCHS and self.bad_epochs >= ENDPOINT_PATIENCE:
            print(
                f"[TEMPORAL endpoint] no calibration-RLS improvement for "
                f"{self.bad_epochs} epochs; stopping."
            )
            self.model.stop_training = True


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
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

    df, class_names = load_filtered_annotations()
    fmap = tc.map_trap_files(tc.TRAPS_DIR)
    X, y_state, meta_list = tc.load_frames(df, fmap)
    trap_orders = tc.build_trap_orders(meta_list)
    y_div, y_dead, human_rls = tc.build_endpoint_targets(meta_list, trap_orders)

    train_keys, cal_keys, test_keys = tc.stratified_trap_split(trap_orders)
    train_idx = tc.indices_for_keys(meta_list, train_keys)
    print(f"--> Split: {len(train_keys)} train / {len(cal_keys)} calibration / "
          f"{len(test_keys)} untouched test traps")

    feat_raw, feat_names, base_div_logits, base_dead_prob = extract_base_features(X, class_names)
    feat, feat_mu, feat_sd = normalize_features(feat_raw, train_idx)

    tr = make_sequence_arrays(feat, base_div_logits, y_div, meta_list, trap_orders, train_keys)
    ca = make_sequence_arrays(feat, base_div_logits, y_div, meta_list, trap_orders, cal_keys)
    te = make_sequence_arrays(feat, base_div_logits, y_div, meta_list, trap_orders, test_keys)

    max_len = tr[1].shape[1]
    print(f"--> Temporal tensor: max_len={max_len}, features={tr[1].shape[-1]}")

    # Base death decoder remains strong; calibrate it ONCE on calibration traps.
    cal_dead_by = flat_prob_by_trap(base_dead_prob, trap_orders, cal_keys)
    death_cfg = tc.calibrate_death_decoder(cal_dead_by, human_rls)

    # Zero-initialized model = direct detector at baseline.  Establish and save
    # that endpoint before a single gradient update.
    model = build_temporal_corrector(max_len, tr[1].shape[-1])
    base_cal_div_by = model_prob_by_trap(model, ca)
    base_div_cfg = tc.calibrate_division_decoder(base_cal_div_by, human_rls)
    _, base_cal_metrics = tc.evaluate_split(
        base_cal_div_by, cal_dead_by, human_rls, base_div_cfg, death_cfg
    )
    base_rank = endpoint_rank(base_cal_metrics)
    model.save_weights(CHECKPOINT)

    print("\n================ CALIBRATION BASELINE (DIRECT DETECTOR) ================")
    print(f"RLS MAE:               {base_cal_metrics['mae']:.2f}")
    print(f"RLS bias:              {base_cal_metrics['bias']:+.2f}")
    print(f"Exact RLS match:       {base_cal_metrics['exact']*100:.1f}%")
    print(f"Within +/-1 division:  {base_cal_metrics['within1']*100:.1f}%")
    print(f"Decoder:               thr={base_div_cfg['threshold']:.2f}, gap={base_div_cfg['min_gap']}")

    cb = EndpointCheckpoint(
        ca, cal_dead_by, human_rls, death_cfg, CHECKPOINT,
        base_rank, base_div_cfg, base_cal_metrics,
    )

    print("\n================ TEMPORAL RESIDUAL TRAINING ================")
    model.fit(
        {"sequence_features": tr[1], "base_division_logit": tr[2]},
        tr[3],
        sample_weight=tr[5],
        validation_data=(
            {"sequence_features": ca[1], "base_division_logit": ca[2]},
            ca[3],
            ca[5],
        ),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[
            cb,
            ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6, verbose=1
            ),
        ],
        verbose=1 if sys.stdout.isatty() else 2,
    )

    model.load_weights(CHECKPOINT)
    chosen_div_cfg = cb.best_div_cfg
    chosen_cal_metrics = cb.best_metrics

    print("\n================ BEST CALIBRATION ENDPOINT ================")
    print(f"Best epoch:            {cb.best_epoch} (0 = original direct detector)")
    print(f"RLS MAE:               {chosen_cal_metrics['mae']:.2f}")
    print(f"RLS bias:              {chosen_cal_metrics['bias']:+.2f}")
    print(f"Exact RLS match:       {chosen_cal_metrics['exact']*100:.1f}%")
    print(f"Within +/-1 division:  {chosen_cal_metrics['within1']*100:.1f}%")
    print(f"Decoder:               thr={chosen_div_cfg['threshold']:.2f}, gap={chosen_div_cfg['min_gap']}")

    # First and only endpoint use of untouched test targets.
    test_div_by = model_prob_by_trap(model, te)
    test_dead_by = flat_prob_by_trap(base_dead_prob, trap_orders, test_keys)
    test_report, test_metrics = tc.evaluate_split(
        test_div_by, test_dead_by, human_rls, chosen_div_cfg, death_cfg
    )
    test_report.to_csv(TEST_REPORT_OUT, index=False)

    print("\n================ UNTOUCHED TEST REPORT: TEMPORAL RESIDUAL ================")
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
        "method": "zero-initialized temporal residual correction of direct division logits",
        "base_state_model": STATE_MODEL,
        "base_rls_model": RLS_MODEL,
        "feature_names": feat_names + ["time_norm", "base_division_probability_delta"],
        "feature_mean": feat_mu.tolist(),
        "feature_std": feat_sd.tolist(),
        "tcn_width": TCN_WIDTH,
        "tcn_dilations": list(TCN_DILATIONS),
        "best_epoch": int(cb.best_epoch),
        "division_decoder": chosen_div_cfg,
        "death_decoder": death_cfg,
        "calibration_metrics": chosen_cal_metrics,
        "test_metrics": test_metrics,
        "deployment_ok": bool(deployment_ok),
        "deployment_gate": {
            "max_test_mae": MAX_DEPLOY_TEST_MAE,
            "min_within1": MIN_DEPLOY_WITHIN1,
            "min_death_agreement": MIN_DEPLOY_DEATH_AGREEMENT,
        },
    }

    model.save(CANDIDATE_MODEL_OUT)
    with open(CANDIDATE_META_OUT, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDEPLOYMENT GATE: {'PASS' if deployment_ok else 'FAIL'} | "
          f"requires MAE<={MAX_DEPLOY_TEST_MAE:.2f}, "
          f"within1>={MIN_DEPLOY_WITHIN1*100:.0f}%, "
          f"death>={MIN_DEPLOY_DEATH_AGREEMENT*100:.0f}%")
    print(f"--> Test concordance: {TEST_REPORT_OUT}")
    print(f"--> Saved candidate temporal corrector: {CANDIDATE_MODEL_OUT}")

    if deployment_ok:
        model.save(PRODUCTION_MODEL_OUT)
        with open(PRODUCTION_META_OUT, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"--> PRODUCTION temporal corrector written: {PRODUCTION_MODEL_OUT}")
        print("\nDONE: temporal residual endpoint gate PASSED.")
    else:
        print("\nTemporal corrector did not clear the production endpoint gate; production artifacts were not overwritten.")
        sys.exit(2)
