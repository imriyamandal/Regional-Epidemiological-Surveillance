"""Classical ML model factory."""

from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from catboost import CatBoostClassifier


def get_classical_models() -> dict:
    return {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
        "extra_trees": ExtraTreesClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
        "xgboost": XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.05, scale_pos_weight=3, random_state=42),
        "lightgbm": LGBMClassifier(n_estimators=200, class_weight="balanced", random_state=42, verbose=-1),
        "catboost": CatBoostClassifier(iterations=200, depth=8, auto_class_weights="Balanced", verbose=0, random_state=42),
    }
