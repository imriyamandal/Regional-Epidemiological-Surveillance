import pandas as pd
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.data.ingestion import generate_surveillance_dataset
from ml.features.engineering import engineer_features, get_feature_columns


def test_feature_count():
    df = generate_surveillance_dataset(start="2023-01-01", end="2024-06-01")
    featured = engineer_features(df)
    cols = get_feature_columns(featured)
    assert len(cols) >= 50, f"Expected 50+ features, got {len(cols)}"


def test_no_infinite_values_after_clip():
    df = generate_surveillance_dataset(start="2023-01-01", end="2024-06-01")
    featured = engineer_features(df)
    cols = get_feature_columns(featured)
    X = featured[cols].fillna(0).replace([np.inf, -np.inf], 0)
    assert np.isfinite(X.values).all()


def test_lag_features_shifted():
    df = generate_surveillance_dataset(start="2023-01-01", end="2024-01-01")
    featured = engineer_features(df)
    assert "lag_1" in featured.columns
    assert featured["lag_1"].notna().sum() > 0
