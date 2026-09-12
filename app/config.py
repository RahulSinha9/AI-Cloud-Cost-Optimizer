from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    aws_region: str = "ap-south-1"
    cost_lookback_days: int = 14
    anomaly_z_threshold: float = 2.5
    max_recommendations: int = 10
    ai_enabled: bool = False
    ai_base_url: str = "http://localhost:11434/v1"
    ai_model: str = "llama3.2"
    ai_api_key: str = ""
    cost_explorer_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
