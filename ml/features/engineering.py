"""Advanced feature engineering — 50+ epidemiological, climate, and geospatial features."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "summer"
    if month in (6, 7, 8, 9):
        return "monsoon"
    return "post_monsoon"


def engineer_features(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    """Generate 50+ features with strict chronological ordering per group."""
    group_cols = group_cols or ["state", "district", "disease_code"]
    df = df.copy()
    df["report_date"] = pd.to_datetime(df["report_date"])
    df = df.sort_values(group_cols + ["report_date"])

    df["month"] = df["report_date"].dt.month
    df["quarter"] = df["report_date"].dt.quarter
    df["year"] = df["report_date"].dt.year
    df["season"] = df["month"].apply(_season)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    g = df.groupby(group_cols, group_keys=False)

    for lag in [1, 2, 3, 6, 12]:
        df[f"lag_{lag}"] = g["case_count"].shift(lag)

    for w in [3, 6]:
        df[f"rolling_mean_{w}"] = g["case_count"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        df[f"rolling_std_{w}"] = g["case_count"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).std())

    shifted = g["case_count"].shift(1)
    df["growth_rate"] = ((df["case_count"] - shifted) / (shifted + 1)).clip(-5, 5)
    df["moving_growth_rate"] = g["case_count"].transform(
        lambda s: s.shift(1).pct_change().rolling(3, min_periods=1).mean()
    )
    df["acceleration"] = g["growth_rate"].diff() if "growth_rate" in df else g["case_count"].transform(
        lambda s: s.shift(1).pct_change().diff()
    )

    threshold = df.groupby(group_cols)["case_count"].transform(lambda s: s.shift(1).quantile(0.75))
    df["outbreak_flag"] = (df["case_count"] > threshold).astype(int)
    df["outbreak_frequency"] = g["outbreak_flag"].transform(
        lambda s: s.shift(1).rolling(12, min_periods=1).mean()
    )
    df["spike_ratio"] = df["case_count"] / (df["rolling_mean_3"] + 1)
    pop = df.get("population", pd.Series(100000, index=df.index))
    df["disease_burden_index"] = df["case_count"] / (pop / 100000 + 1)
    df["outbreak_memory"] = g["outbreak_flag"].transform(lambda s: s.shift(1).ewm(span=6).mean())
    df["outbreak_streak"] = g["outbreak_flag"].transform(
        lambda s: s.shift(1).groupby((s.shift(1) != s.shift(1).shift()).cumsum()).cumcount() + 1
    )

    for col in ["temperature", "rainfall", "humidity", "precipitation", "leaf_area_index"]:
        if col in df.columns:
            df[f"{col}_change"] = g[col].diff()
        else:
            df[col] = np.nan
            df[f"{col}_change"] = np.nan

    state_g = df.groupby(["state", "disease_code", "report_date"], as_index=False)
    district_counts = state_g["district"].nunique().rename(columns={"district": "district_count"})
    df = df.merge(district_counts, on=["state", "disease_code", "report_date"], how="left")
    total_cases = state_g["case_count"].sum().rename(columns={"case_count": "state_total"})
    df = df.merge(total_cases, on=["state", "disease_code", "report_date"], how="left")
    df["concentration_ratio"] = df["case_count"] / (df["state_total"] + 1)
    df["district_expansion"] = g["district"].transform(lambda s: s.shift(1).nunique())
    df["geo_spread"] = df["district_count"] / (df["district_count"].max() + 1)
    df["cluster_density"] = df["case_count"] * df["concentration_ratio"]

    df["yoy_change"] = g["case_count"].pct_change(periods=12)
    df["moving_trend"] = g["case_count"].transform(lambda s: s.shift(1).rolling(6).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0, raw=False))
    df["disease_velocity"] = df["growth_rate"].diff()
    df["disease_momentum"] = df["rolling_mean_3"] * df["growth_rate"]
    df["risk_velocity"] = df["growth_rate"].rolling(3, min_periods=1).mean()

    if "population_density" not in df.columns and "population" in df.columns:
        df["population_density"] = df["population"] / 100

    df["target_outbreak"] = (df["risk_score"] >= 0.5).astype(int) if "risk_score" in df.columns else (
        df["case_count"] > df.groupby(group_cols)["case_count"].transform(lambda s: s.shift(1).quantile(0.8))
    ).astype(int)

    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    exclude = {
        "id", "report_date", "target_outbreak", "risk_score", "disease_id",
        "state", "district", "disease_code", "season", "source", "metadata_json",
        "death_count", "outbreak_flag",
    }
    numeric = df.select_dtypes(include=[np.number]).columns
    return [c for c in numeric if c not in exclude and not c.startswith("target")]
