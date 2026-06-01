"""Lightweight ML training (no TensorFlow/CatBoost) for local dev."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN
from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.data.ingestion import generate_surveillance_dataset, save_processed
from ml.evaluation.leakage_audit import audit_temporal_leakage, save_audit_report
from ml.features.engineering import engineer_features, get_feature_columns

ARTIFACTS = ROOT / "backend" / "artifacts"


def evaluate_model(model, X_test, y_test) -> dict:
    proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test)
    pred = (proba >= 0.5).astype(int) if hasattr(proba, "ndim") else model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)) if len(np.unique(y_test)) > 1 else 0.0,
    }


def run_pipeline():
    mlruns = (ROOT / "mlruns").resolve()
    mlruns.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(mlruns.as_uri())
    mlflow.set_experiment("dopewis-outbreak-prediction")

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
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    save_audit_report(audit, ARTIFACTS / "leakage_audit.json")
    print(f"Leakage audit passed: {audit.passed}")

    X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0).clip(-1e6, 1e6)
    y = df["target_outbreak"]
    train_idx, test_idx = list(TimeSeriesSplit(n_splits=5).split(X))[-1]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=100, max_depth=10, class_weight="balanced", random_state=42),
        "extra_trees": ExtraTreesClassifier(n_estimators=100, max_depth=10, class_weight="balanced", random_state=42),
        "xgboost": XGBClassifier(n_estimators=100, max_depth=6, scale_pos_weight=3, eval_metric="logloss", random_state=42),
        "lightgbm": LGBMClassifier(n_estimators=100, class_weight="balanced", random_state=42, verbose=-1),
    }
    resamplers = {"none": None, "smote": SMOTE(random_state=42), "borderline_smote": BorderlineSMOTE(random_state=42), "adasyn": ADASYN(random_state=42)}

    best_model, best_score, best_name, results = None, -1.0, "", {}

    with mlflow.start_run(run_name="dopewis-local-pipeline"):
        mlflow.log_param("n_features", len(feature_cols))
        for res_name, resampler in resamplers.items():
            Xr, yr = resampler.fit_resample(X_train, y_train) if resampler else (X_train, y_train)
            for model_name, model in models.items():
                model.fit(Xr, yr)
                metrics = evaluate_model(model, X_test, y_test)
                results[f"{model_name}_{res_name}"] = metrics
                mlflow.log_metrics({f"{model_name}_{res_name}_{k}": v for k, v in metrics.items()})
                if metrics["roc_auc"] > best_score:
                    best_score, best_model, best_name = metrics["roc_auc"], model, f"{model_name}_{res_name}"

        smote = SMOTE(random_state=42)
        Xs, ys = smote.fit_resample(X_train, y_train)
        stack = StackingClassifier(
            estimators=[
                ("xgb", XGBClassifier(n_estimators=80, scale_pos_weight=3, random_state=42)),
                ("lgb", LGBMClassifier(n_estimators=80, verbose=-1, random_state=42)),
                ("rf", RandomForestClassifier(n_estimators=80, random_state=42)),
            ],
            final_estimator=LogisticRegression(max_iter=1000),
            cv=3,
        )
        stack.fit(Xs, ys)
        stack_metrics = evaluate_model(stack, X_test, y_test)
        results["stacking_ensemble"] = stack_metrics
        if stack_metrics["roc_auc"] > best_score:
            best_score, best_model, best_name = stack_metrics["roc_auc"], stack, "stacking_ensemble"

        voting = VotingClassifier(
            estimators=[
                ("xgb", XGBClassifier(n_estimators=60, random_state=42)),
                ("lgb", LGBMClassifier(n_estimators=60, verbose=-1, random_state=42)),
            ],
            voting="soft",
        )
        voting.fit(Xs, ys)
        results["voting_ensemble"] = evaluate_model(voting, X_test, y_test)

        importances = {}
        if hasattr(best_model, "feature_importances_"):
            importances = dict(zip(feature_cols, best_model.feature_importances_.tolist()))

        joblib.dump(best_model, ARTIFACTS / "best_model.joblib")
        meta = {"feature_columns": feature_cols, "best_model_name": best_name, "best_roc_auc": best_score, "feature_importance": importances, "all_results": results}
        joblib.dump(meta, ARTIFACTS / "model_meta.joblib")
        (ARTIFACTS / "training_results.json").write_text(json.dumps(results, indent=2))
        mlflow.sklearn.log_model(best_model, "best_model")

    print(f"Best model: {best_name} (ROC-AUC: {best_score:.4f})")
    return best_model, meta


if __name__ == "__main__":
    run_pipeline()
