"""Leakage audit module — fold-based statistics and chronological validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit


@dataclass
class LeakageAuditReport:
    passed: bool
    issues: list[str] = field(default_factory=list)
    fold_stats: list[dict[str, Any]] = field(default_factory=list)
    threshold_checks: dict[str, bool] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "issues": self.issues,
            "fold_stats": self.fold_stats,
            "threshold_checks": self.threshold_checks,
            "generated_at": self.generated_at,
        }


def audit_temporal_leakage(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str = "target_outbreak",
    date_col: str = "report_date",
    n_splits: int = 5,
) -> LeakageAuditReport:
    """Verify no future information leaks into training folds."""
    issues: list[str] = []
    fold_stats: list[dict] = []
    df = df.sort_values(date_col).reset_index(drop=True)

    for col in feature_cols:
        if col.startswith("lag_") or "rolling" in col or "shift" in col:
            continue
        if df[col].isna().mean() < 0.01 and df[col].corr(df[target_col]) > 0.99:
            issues.append(f"Suspicious near-perfect correlation: {col}")

    tscv = TimeSeriesSplit(n_splits=n_splits)
    X = df[feature_cols].fillna(0)
    y = df[target_col]

    for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X)):
        train_dates = df.iloc[train_idx][date_col]
        test_dates = df.iloc[test_idx][date_col]
        if train_dates.max() >= test_dates.min():
            issues.append(f"Fold {fold_idx}: train max date >= test min date (temporal leak)")
        fold_stats.append(
            {
                "fold": fold_idx,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
                "train_end": str(train_dates.max()),
                "test_start": str(test_dates.min()),
                "train_positive_rate": float(y.iloc[train_idx].mean()),
                "test_positive_rate": float(y.iloc[test_idx].mean()),
            }
        )

    threshold_checks = {
        "chronological_order": len(issues) == 0 or all("temporal leak" not in i for i in issues),
        "no_perfect_features": not any("near-perfect" in i for i in issues),
    }
    passed = len(issues) == 0 and all(threshold_checks.values())
    return LeakageAuditReport(passed=passed, issues=issues, fold_stats=fold_stats, threshold_checks=threshold_checks)


def save_audit_report(report: LeakageAuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2))
