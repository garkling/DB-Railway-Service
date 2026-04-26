from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "mysql+pymysql://root:railway@localhost:3306/railway_service"
    DEBUG: bool = False
    TEMPLATE_DIR: Path = Path("app/templates")
    STATIC_DIR: Path = Path("app/static")


settings = Settings()
