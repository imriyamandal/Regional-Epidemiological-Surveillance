"""Full ML training pipeline: classical, time-series, deep learning, ensembles, MLflow."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import ADASYN, BorderlineSMOTE, SMOTE
from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.data.ingestion import generate_surveillance_dataset, save_processed  # noqa: E402
from ml.evaluation.leakage_audit import audit_temporal_leakage, save_audit_report  # noqa: E402
from ml.features.engineering import engineer_features, get_feature_columns  # noqa: E402

ARTIFACTS = ROOT / "backend" / "artifacts"
MLFLOW_EXPERIMENT = "dopewis-outbreak-prediction"


def build_classical_models() -> dict:
    return {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
        "extra_trees": ExtraTreesClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
        "xgboost": XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.05,
            scale_pos_weight=3, eval_metric="logloss", random_state=42,
        ),
        "lightgbm": LGBMClassifier(n_estimators=200, class_weight="balanced", random_state=42, verbose=-1),
        "catboost": CatBoostClassifier(iterations=200, depth=8, auto_class_weights="Balanced", verbose=0, random_state=42),
    }


def evaluate_model(model, X_test, y_test) -> dict:
    proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test)
    pred = (proba >= 0.5).astype(int) if proba.ndim else model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)) if len(np.unique(y_test)) > 1 else 0.0,
    }


def train_lstm_stub(X_train, y_train, X_test, y_test) -> dict:
    """LSTM training requires sequence windows; returns baseline metrics for registry."""
    try:
        import tensorflow as tf
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, GRU

        seq_len = min(6, X_train.shape[1])
        def reshape(X):
            n = X.shape[0]
            f = X.shape[1]
            pad = seq_len - (f % seq_len) if f % seq_len else 0
            if pad:
                X = np.pad(X, ((0, 0), (0, pad)))
            return X.reshape(n, -1, seq_len)

        Xtr, Xte = reshape(X_train.values), reshape(X_test.values)
        model = Sequential([
            Bidirectional(LSTM(32, return_sequences=True), input_shape=(Xtr.shape[1], Xtr.shape[2])),
            Dropout(0.2),
            GRU(16),
            Dense(1, activation="sigmoid"),
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        model.fit(Xtr, y_train, epochs=15, batch_size=64, verbose=0, validation_split=0.1)
        proba = model.predict(Xte, verbose=0).ravel()
        pred = (proba >= 0.5).astype(int)
        return {
            "accuracy": float(accuracy_score(y_test, pred)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, proba)) if len(np.unique(y_test)) > 1 else 0.0,
            "model": model,
        }
    except Exception as e:
        return {"accuracy": 0.0, "f1": 0.0, "roc_auc": 0.0, "error": str(e)}


def run_pipeline():
    mlruns = (ROOT / "mlruns").resolve()
    mlruns.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", mlruns.as_uri()))
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    raw_path = ROOT / "ml" / "data" / "processed" / "surveillance.parquet"
    if not raw_path.exists():
        df_raw = generate_surveillance_dataset()
        save_processed(df_raw, raw_path)
    else:
        df_raw = pd.read_parquet(raw_path)

    df = engineer_features(df_raw)
    feature_cols = get_feature_columns(df)
    df = df.dropna(subset=feature_cols + ["target_outbreak"]).reset_index(drop=True)

    audit = audit_temporal_leakage(df, feature_cols)
    save_audit_report(audit, ARTIFACTS / "leakage_audit.json")
    print(f"Leakage audit passed: {audit.passed}")

    X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0).clip(-1e6, 1e6)
    y = df["target_outbreak"]

    tscv = TimeSeriesSplit(n_splits=5)
    train_idx, test_idx = list(tscv.split(X))[-1]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    resamplers = {
        "none": None,
        "smote": SMOTE(random_state=42),
        "borderline_smote": BorderlineSMOTE(random_state=42),
        "adasyn": ADASYN(random_state=42),
    }

    best_model = None
    best_score = -1
    best_name = ""
    results = {}

    with mlflow.start_run(run_name="dopewis-full-pipeline") as parent_run:
        mlflow.log_param("n_features", len(feature_cols))
        mlflow.log_param("n_samples", len(df))
        mlflow.log_param("leakage_passed", audit.passed)

        for res_name, resampler in resamplers.items():
            Xr, yr = (resampler.fit_resample(X_train, y_train) if resampler else (X_train, y_train))
            for model_name, model in build_classical_models().items():
                with mlflow.start_run(run_name=f"{model_name}_{res_name}", nested=True):
                    model.fit(Xr, yr)
                    metrics = evaluate_model(model, X_test, y_test)
                    for k, v in metrics.items():
                        mlflow.log_metric(k, v)
                    mlflow.log_param("resampler", res_name)
                    mlflow.sklearn.log_model(model, model_name)
                    results[f"{model_name}_{res_name}"] = metrics
                    if metrics["roc_auc"] > best_score:
                        best_score = metrics["roc_auc"]
                        best_model = model
                        best_name = f"{model_name}_{res_name}"

        # Stacking ensemble
        estimators = [
            ("xgb", XGBClassifier(n_estimators=100, scale_pos_weight=3, random_state=42)),
            ("lgb", LGBMClassifier(n_estimators=100, verbose=-1, random_state=42)),
            ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
        ]
        stack = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(max_iter=1000),
            cv=3,
        )
        smote = SMOTE(random_state=42)
        Xs, ys = smote.fit_resample(X_train, y_train)
        stack.fit(Xs, ys)
        stack_metrics = evaluate_model(stack, X_test, y_test)
        mlflow.sklearn.log_model(stack, "stacking_ensemble")
        if stack_metrics["roc_auc"] > best_score:
            best_score = stack_metrics["roc_auc"]
            best_model = stack
            best_name = "stacking_ensemble"

        voting = VotingClassifier(
            estimators=[("xgb", XGBClassifier(n_estimators=80, random_state=42)),
                        ("lgb", LGBMClassifier(n_estimators=80, verbose=-1, random_state=42))],
            voting="soft",
        )
        voting.fit(Xs, ys)
        vote_metrics = evaluate_model(voting, X_test, y_test)
        results["voting_ensemble"] = vote_metrics

        lstm_metrics = train_lstm_stub(X_train, y_train, X_test, y_test)
        mlflow.log_metrics({f"lstm_{k}": v for k, v in lstm_metrics.items() if isinstance(v, (int, float))})

        importances = {}
        if hasattr(best_model, "feature_importances_"):
            importances = dict(zip(feature_cols, best_model.feature_importances_.tolist()))

        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_model, ARTIFACTS / "best_model.joblib")
        meta = {
            "feature_columns": feature_cols,
            "best_model_name": best_name,
            "best_roc_auc": best_score,
            "feature_importance": importances,
            "all_results": results,
        }
        joblib.dump(meta, ARTIFACTS / "model_meta.joblib")
        (ARTIFACTS / "training_results.json").write_text(json.dumps(results, indent=2))
        mlflow.log_artifact(str(ARTIFACTS / "leakage_audit.json"))

    print(f"Best model: {best_name} (ROC-AUC: {best_score:.4f})")
    return best_model, meta


if __name__ == "__main__":
    run_pipeline()
