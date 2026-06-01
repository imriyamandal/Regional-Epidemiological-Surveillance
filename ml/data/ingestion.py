"""Data ingestion from IDSP-style surveillance, WHO patterns, and climate APIs."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

DISEASES = ["DENGUE", "MALARIA", "CHOLERA", "CHIKUNGUNYA", "AES", "ADD"]

INDIA_STATES_DISTRICTS = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Mangaluru", "Hubballi"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri"],
    "Uttar Pradesh": ["Lucknow", "Varanasi", "Kanpur", "Agra"],
    "Delhi": ["Central Delhi", "South Delhi", "North Delhi"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
}

DISTRICT_COORDS = {
    ("Maharashtra", "Pune"): (18.5204, 73.8567),
    ("Maharashtra", "Mumbai"): (19.0760, 72.8777),
    ("Kerala", "Kochi"): (9.9312, 76.2673),
    ("Karnataka", "Bengaluru Urban"): (12.9716, 77.5946),
    ("Tamil Nadu", "Chennai"): (13.0827, 80.2707),
    ("West Bengal", "Kolkata"): (22.5726, 88.3639),
    ("Delhi", "Central Delhi"): (28.6328, 77.2197),
    ("Gujarat", "Ahmedabad"): (23.0225, 72.5714),
}


def _default_coords(state: str, district: str) -> tuple[float, float]:
    return DISTRICT_COORDS.get((state, district), (20.5937 + np.random.uniform(-5, 5), 78.9629 + np.random.uniform(-5, 5)))


def generate_surveillance_dataset(
    start: str = "2018-01-01",
    end: str = "2025-12-01",
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate realistic India district-level surveillance data calibrated to
    IDSP/WHO disease seasonality. Replace with CSV from data.gov.in IDSP when available.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="MS")
    rows = []

    for state, districts in INDIA_STATES_DISTRICTS.items():
        for district in districts:
            lat, lon = _default_coords(state, district)
            pop = int(rng.integers(200_000, 5_000_000))
            density = pop / rng.uniform(50, 500)

            for disease in DISEASES:
                base = {"DENGUE": 80, "MALARIA": 40, "CHOLERA": 15, "CHIKUNGUNYA": 25, "AES": 10, "ADD": 60}[disease]
                level = rng.uniform(0.5, 2.0)
                memory = base * level

                for dt in dates:
                    month = dt.month
                    seasonal = 1 + 0.6 * np.sin(2 * np.pi * (month - 6) / 12)
                    if disease in ("DENGUE", "CHIKUNGUNYA", "MALARIA"):
                        seasonal = 1 + 0.8 * np.sin(2 * np.pi * (month - 8) / 12)
                    noise = rng.lognormal(0, 0.35)
                    cases = max(0, int(memory * seasonal * noise))
                    memory = 0.7 * memory + 0.3 * cases

                    temp = 22 + 8 * np.sin(2 * np.pi * month / 12) + rng.normal(0, 1.5)
                    rain = max(0, 150 * np.sin(2 * np.pi * (month - 6) / 12) + rng.normal(50, 30))
                    humidity = min(100, max(30, 60 + rng.normal(0, 10)))

                    rows.append(
                        {
                            "state": state,
                            "district": district,
                            "disease_code": disease,
                            "report_date": dt,
                            "case_count": cases,
                            "death_count": max(0, int(cases * rng.uniform(0, 0.02))),
                            "population": pop,
                            "population_density": density,
                            "latitude": lat + rng.normal(0, 0.05),
                            "longitude": lon + rng.normal(0, 0.05),
                            "temperature": temp,
                            "rainfall": rain,
                            "humidity": humidity,
                            "precipitation": rain * 0.9,
                            "wind_speed": rng.uniform(2, 15),
                            "air_quality_index": rng.uniform(50, 300),
                            "leaf_area_index": rng.uniform(0.2, 0.9),
                            "source": "IDSP_SYNTHETIC",
                        }
                    )

    return pd.DataFrame(rows)


def load_idsp_csv(path: Path) -> pd.DataFrame:
    """Load real IDSP export when provided by user."""
    return pd.read_csv(path, parse_dates=["report_date"])


def save_processed(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "processed" / "surveillance.parquet"
    df = generate_surveillance_dataset()
    save_processed(df, out)
    print(f"Saved {len(df)} records to {out}")
