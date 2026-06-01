"""Scheduled retraining pipeline for MLOps."""

from ml.training.pipeline_local import run_pipeline

if __name__ == "__main__":
    print("Starting DOPEWIS model retraining...")
    run_pipeline()
    print("Retraining complete.")
