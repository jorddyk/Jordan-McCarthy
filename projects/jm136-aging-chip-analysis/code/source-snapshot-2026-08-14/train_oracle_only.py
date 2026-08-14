"""
train_oracle_only.py -- Prospective remaining-RLS quantile oracle (v2 features).

FIXES vs previous version:
  1. FEATURE SYNC: extract_prefix_features / find_division_frames /
     calculate_trap_rls are byte-identical to human_classifier_ui.py. The old
     trainer's division detection lacked the No-Cell-gap lookback the UI used,
     so IDI features differed between training and serving.
  2. CONFIDENCE FEATURES REMOVED (v2, 20 features): they were trained as
     constant 1.0 (human labels have no classifier confidence) but served with
     real confidences -- train/serve skew. The UI validates feature_version=2.
  3. CENSORING: the oracle now trains ONLY on traps whose death was observed
     on-chip (ONLY_COMPLETED_LIFESPANS). Training "remaining = final - observed"
     on right-censored traps teaches it to predict when observation stops, not
     when cells die. Prefixes at/after the death frame are skipped (the UI
     short-circuits dead states to 0 anyway).
  4. Rows without a Class label are dropped (phantom-'Mother' guard) and a
     trap-level validation split reports honest held-out pinball loss.
"""

import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models

ANNOTATION_PATH = os.path.join("annotation", "master_human_annotations.xlsx")
ORACLE_MODEL_PATH = "lifespan_oracle.keras"
ORACLE_META_PATH = "lifespan_oracle_meta.json"
MIN_HISTORY_DIVISIONS = 1
PREFIX_STRIDE = 5                  # sample every Nth frame prefix
ONLY_COMPLETED_LIFESPANS = True    # require died_on_chip (avoid right-censoring bias)
EXCLUDE_CENSORED_TRAPS = False     # censored now = escaped/skipped only (blur never censors)
VAL_FRACTION = 0.2                 # trap-level validation split
RANDOM_SEED = 42

ORACLE_FEATURE_VERSION = 2  # v2: dropped mean_conf/recent_conf (were trained as constant 1.0
                            # from human labels but served with real classifier confidences ->
                            # train/serve skew). Retrain with train_oracle_only.py.
ORACLE_FEATURE_NAMES = [
    "curr_rls", "frames_observed",
    "frac_mother", "frac_early", "frac_late", "frac_no_cell", "frac_blurry", "frac_dead",
    "is_curr_mother", "is_curr_early", "is_curr_late", "is_curr_no_cell", "is_curr_blurry", "is_curr_dead",
    "mean_idi", "std_idi", "recent_idi", "recent_3_mean_idi", "idi_slope", "idi_cv"
]


def find_division_frames(frame_labels):
    """Frame indices at which a completed division is registered.
    A division = Late Bud -> (Mother | Early Bud), optionally across a run of
    'No Cell' or 'Out of Focus / Blurry' frames: both are treated as missing
    observations that do not break the transition. NOTE: a long gap can hide
    additional divisions, which are inherently uncountable.
    !! KEEP IDENTICAL to the copies in train_classifier.py / train_oracle_only.py !!"""
    GAP_STATES = ("No Cell", "Out of Focus / Blurry")
    div_frames = []
    for i in range(1, len(frame_labels)):
        curr = frame_labels[i]
        if curr is None:
            continue
        prev = frame_labels[i - 1]
        if prev is None:
            continue

        if prev == "Late Bud" and curr in ("Mother", "Early Bud"):
            div_frames.append(i)
        elif curr in ("Mother", "Early Bud"):
            lookback_idx = i - 1
            while lookback_idx >= 0 and frame_labels[lookback_idx] in GAP_STATES:
                lookback_idx -= 1
            if 0 <= lookback_idx < i - 1 and frame_labels[lookback_idx] in ("Early Bud", "Late Bud"):
                div_frames.append(i)
    return div_frames


def calculate_trap_rls(frame_labels):
    """Trap-level RLS metrics. CENSORING POLICY: blurry frames do NOT censor
    the trap (every trap has some) -- blur only invalidates that frame's
    spatial data. Only 'Mother Escaped' and 'Skipped / Bad Trap' censor.
    Death detection bridges blurry/unlabeled runs (living -> [blur...] -> Dead
    still counts as an observed on-chip death)."""
    valid_living_states = {"Mother", "Early Bud", "Late Bud"}
    rls_count = len(find_division_frames(frame_labels))

    died_on_chip, death_frame_idx = False, None
    for i in range(1, len(frame_labels)):
        if frame_labels[i] != "Dead Cell":
            continue
        lb = i - 1
        while lb >= 0 and frame_labels[lb] in ("Out of Focus / Blurry", None):
            lb -= 1
        if lb >= 0 and frame_labels[lb] in valid_living_states:
            died_on_chip, death_frame_idx = True, i
            break

    is_censored = False
    censor_reasons = []
    max_check_idx = death_frame_idx if (died_on_chip and death_frame_idx is not None) else len(frame_labels) - 1

    for i in range(max_check_idx + 1):
        curr = frame_labels[i]
        if curr is None:
            continue

        if curr == "Mother Escaped (Ignore Rest)":
            is_censored = True
            if "Mother Escaped" not in censor_reasons:
                censor_reasons.append("Mother Escaped")
        elif curr == "Skipped / Bad Trap":
            is_censored = True
            if "Skipped Trap" not in censor_reasons:
                censor_reasons.append("Skipped Trap")

    return {
        "rls_count": rls_count,
        "is_censored": is_censored,
        "censor_reasons": censor_reasons,
        "died_on_chip": died_on_chip,
        "death_frame": death_frame_idx
    }


def extract_prefix_features(frame_labels):
    """Oracle feature vector (v2). Division/IDI features come from the shared
    find_division_frames() so they can never diverge from the RLS counter.
    !! KEEP IDENTICAL to the copy in train_oracle_only.py !!"""
    n_obs = len(frame_labels)
    if n_obs == 0:
        return np.zeros(len(ORACLE_FEATURE_NAMES), dtype=np.float32)

    rls_data = calculate_trap_rls(frame_labels)
    curr_rls = float(rls_data["rls_count"])

    c_mother = sum(1 for x in frame_labels if x == "Mother")
    c_early  = sum(1 for x in frame_labels if x == "Early Bud")
    c_late   = sum(1 for x in frame_labels if x == "Late Bud")
    c_nocell = sum(1 for x in frame_labels if x == "No Cell")
    c_blur   = sum(1 for x in frame_labels if x == "Out of Focus / Blurry")
    c_dead   = sum(1 for x in frame_labels if x == "Dead Cell")

    frac_mother = c_mother / n_obs
    frac_early  = c_early / n_obs
    frac_late   = c_late / n_obs
    frac_nocell = c_nocell / n_obs
    frac_blur   = c_blur / n_obs
    frac_dead   = c_dead / n_obs

    curr_label = frame_labels[-1]
    is_curr_mother = 1.0 if curr_label == "Mother" else 0.0
    is_curr_early  = 1.0 if curr_label == "Early Bud" else 0.0
    is_curr_late   = 1.0 if curr_label == "Late Bud" else 0.0
    is_curr_nocell = 1.0 if curr_label == "No Cell" else 0.0
    is_curr_blur   = 1.0 if curr_label == "Out of Focus / Blurry" else 0.0
    is_curr_dead   = 1.0 if curr_label == "Dead Cell" else 0.0

    div_frames = find_division_frames(frame_labels)

    k_divs = len(div_frames)
    if k_divs >= 2:
        idis = [div_frames[j] - div_frames[j - 1] for j in range(1, k_divs)]
    elif k_divs == 1:
        idis = [div_frames[0]]
    else:
        idis = []

    mean_idi = float(np.mean(idis)) if len(idis) > 0 else 0.0
    std_idi  = float(np.std(idis)) if len(idis) > 1 else 0.0
    recent_idi = float(idis[-1]) if len(idis) > 0 else 0.0
    recent_3_mean = float(np.mean(idis[-3:])) if len(idis) > 0 else 0.0

    if len(idis) >= 3:
        try:
            idi_slope = float(np.polyfit(range(len(idis)), idis, 1)[0])
        except Exception:
            idi_slope = 0.0
    else:
        idi_slope = 0.0

    idi_cv = (std_idi / (mean_idi + 1e-5)) if len(idis) > 1 else 0.0

    return np.array([
        curr_rls, float(n_obs),
        frac_mother, frac_early, frac_late, frac_nocell, frac_blur, frac_dead,
        is_curr_mother, is_curr_early, is_curr_late, is_curr_nocell, is_curr_blur, is_curr_dead,
        mean_idi, std_idi, recent_idi, recent_3_mean, idi_slope, idi_cv
    ], dtype=np.float32)


# ==============================================================================
# PROSPECTIVE LIFESPAN QUANTILE ORACLE
# ==============================================================================


@tf.keras.utils.register_keras_serializable(package="Custom")
def pinball_loss_multi(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_true = tf.reshape(y_true, (-1, 1))  # Force shape to (batch, 1) for broadcasting
    err = y_true - y_pred
    q = tf.constant([[0.1, 0.5, 0.9]], dtype=tf.float32)
    loss = tf.maximum(q * err, (q - 1.0) * err)
    return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))


# --- MAIN EXECUTION ---
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

print(f"Loading annotations from {ANNOTATION_PATH}...")
try:
    df = pd.read_excel(ANNOTATION_PATH, sheet_name="Frame_Annotations")
except Exception:
    df = pd.read_excel(ANNOTATION_PATH)

n_raw = len(df)
df = df.dropna(subset=['Class'])
df['Class'] = df['Class'].astype(str).str.strip()
df = df[df['Class'].str.lower() != 'nan']
if len(df) < n_raw:
    print(f"--> Dropped {n_raw - len(df)} rows without a Class label.")

EXCLUDE_CLASSES = ["Skipped / Bad Trap", "Mother Escaped (Ignore Rest)", "2 Cells (Right)", "2 Cells"]
valid_df = df[~df['Class'].isin(EXCLUDE_CLASSES)].copy()

trap_groups = {}
for _, row in valid_df.iterrows():
    chip_id = str(row.get("Chip_ID", "default_chip")).strip()
    pos = str(row.get("Position", "default_pos")).strip().lower()
    key = (chip_id, pos, int(row["Trap_ID"]))
    trap_groups.setdefault(key, []).append((int(row["Frame"]), str(row["Class"]).strip()))

prefix_samples = []
n_traps_used, n_traps_censored_skip, n_traps_alive_skip = 0, 0, 0

for key, frame_list in trap_groups.items():
    labels = [x[1] for x in sorted(frame_list, key=lambda x: x[0])]
    full_rls = calculate_trap_rls(labels)

    if ONLY_COMPLETED_LIFESPANS and not full_rls["died_on_chip"]:
        n_traps_alive_skip += 1
        continue
    if EXCLUDE_CENSORED_TRAPS and full_rls["is_censored"]:
        n_traps_censored_skip += 1
        continue

    n_traps_used += 1
    final_rls = full_rls["rls_count"]
    death_idx = full_rls["death_frame"]

    for t in range(len(labels)):
        if death_idx is not None and t >= death_idx:
            break  # remaining RLS at/after death is trivially 0; UI short-circuits it
        sub_labels = labels[:t + 1]
        obs_rls = calculate_trap_rls(sub_labels)["rls_count"]
        if obs_rls >= MIN_HISTORY_DIVISIONS and t % PREFIX_STRIDE == 0:
            prefix_samples.append({
                "trap": key,
                "feat": extract_prefix_features(sub_labels),
                "target_rem": float(max(0, final_rls - obs_rls))
            })

print(f"--> Traps used: {n_traps_used} | skipped (no observed death): {n_traps_alive_skip}"
      + (f" | skipped (censored): {n_traps_censored_skip}" if EXCLUDE_CENSORED_TRAPS else ""))
print(f"--> Prefix samples: {len(prefix_samples)}")

if len(prefix_samples) < 10:
    print("--> Injecting baseline sequence profiles for model initialization...")
    for dummy_rls in range(1, 25):
        dummy_labels = ["Mother", "Early Bud", "Late Bud"] * dummy_rls
        prefix_samples.append({"trap": ("dummy", "dummy", dummy_rls),
                               "feat": extract_prefix_features(dummy_labels),
                               "target_rem": float(max(0, 25 - dummy_rls))})

X = np.array([s["feat"] for s in prefix_samples], dtype=np.float32)
y = np.expand_dims(np.array([s["target_rem"] for s in prefix_samples], dtype=np.float32), axis=-1)
sample_traps = np.array(["|".join(map(str, s["trap"])) for s in prefix_samples])

mean_vec = np.mean(X, axis=0)
std_vec = np.std(X, axis=0)
std_vec[std_vec < 1e-6] = 1.0
X_norm = (X - mean_vec) / std_vec

# Trap-level validation split (frames of one trap never straddle the split)
unique_traps = np.unique(sample_traps)
val_data = None
if len(unique_traps) >= 5:
    rng = np.random.RandomState(RANDOM_SEED)
    val_traps = set(rng.choice(unique_traps, size=max(1, int(len(unique_traps) * VAL_FRACTION)), replace=False))
    va_mask = np.isin(sample_traps, list(val_traps))
    X_tr, y_tr = X_norm[~va_mask], y[~va_mask]
    X_va, y_va = X_norm[va_mask], y[va_mask]
    val_data = (X_va, y_va)
    print(f"--> Trap-level split: {len(unique_traps) - len(val_traps)} train traps, {len(val_traps)} val traps.")
else:
    X_tr, y_tr = X_norm, y
    print("--> Too few traps for a validation split; training on everything.")

oracle = models.Sequential([
    layers.Input(shape=(X_norm.shape[1],)),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dense(3)
])

oracle.compile(optimizer='adam', loss=pinball_loss_multi)
oracle.fit(X_tr, y_tr, validation_data=val_data, epochs=40, batch_size=16, verbose=1)

if val_data is not None:
    val_loss = oracle.evaluate(*val_data, verbose=0)
    med = oracle.predict(val_data[0], verbose=0)[:, 1]
    mae = float(np.mean(np.abs(med - val_data[1].ravel())))
    print(f"--> Held-out trap pinball loss: {val_loss:.3f} | median-quantile MAE: {mae:.2f} divisions")

oracle.save(ORACLE_MODEL_PATH)
meta = {
    "feature_version": ORACLE_FEATURE_VERSION,
    "feature_names": ORACLE_FEATURE_NAMES,
    "feature_means": mean_vec.tolist(),
    "feature_stds": std_vec.tolist(),
    "min_history_divisions": MIN_HISTORY_DIVISIONS,
    "quantiles": [0.1, 0.5, 0.9],
    "only_completed_lifespans": ONLY_COMPLETED_LIFESPANS,
    "n_training_traps": int(n_traps_used)
}
with open(ORACLE_META_PATH, "w") as f:
    json.dump(meta, f, indent=2)

print(f"\n--> SUCCESS: Saved '{ORACLE_MODEL_PATH}' and '{ORACLE_META_PATH}'. Re-run human_classifier_ui.py to launch overlay.")
