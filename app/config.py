from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hubaooo's Warehouse API"
    app_env: str = "development"
    database_url: str = "sqlite:///./warehouse.db"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    jwt_secret: str = "development-only-change-this-secret-key"
    access_token_expire_minutes: int = 120
    upload_dir: str = "uploads"
    max_upload_mb: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
