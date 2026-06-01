from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DOPEWIS"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./dopewis.db"
    database_url_sync: str = "sqlite:///./dopewis.db"

    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "dopewis-outbreak-prediction"
    model_artifacts_path: str = "artifacts"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = "alerts@dopewis.health"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    rate_limit_per_minute: int = 120

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
