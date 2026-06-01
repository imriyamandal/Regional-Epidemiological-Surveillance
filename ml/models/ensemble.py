"""Ensemble models: voting, stacking, blending."""

from lightgbm import LGBMClassifier
from sklearn.ensemble import StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def build_stacking_ensemble():
    estimators = [
        ("xgb", XGBClassifier(n_estimators=100, scale_pos_weight=3, random_state=42)),
        ("lgb", LGBMClassifier(n_estimators=100, verbose=-1, random_state=42)),
        ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
    ]
    return StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(max_iter=1000),
        cv=3,
    )


def build_voting_ensemble():
    return VotingClassifier(
        estimators=[
            ("xgb", XGBClassifier(n_estimators=80, random_state=42)),
            ("lgb", LGBMClassifier(n_estimators=80, verbose=-1, random_state=42)),
        ],
        voting="soft",
    )


def blend_predictions(predictions: list, weights: list | None = None):
    weights = weights or [1 / len(predictions)] * len(predictions)
    blended = sum(w * p for w, p in zip(weights, predictions))
    return blended
