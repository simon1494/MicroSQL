from pydantic import AliasChoices, Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str | None = None

    AUTH_HOST: str | None = None
    AUTH_PORT: int | None = None
    AUTH_KEY: str | None = "clave"

    WORKERS: int = Field(
        default=1, validation_alias=AliasChoices("APP_WORKERS", "WORKERS")
    )

    RELOAD: bool = False
    LOGGER: bool = False
    LOGGER_LEVEL: str | None = None

    SESSION_EXPIRE: int = Field(..., validation_alias=AliasChoices("SESSION_EXPIRE"))

    HELIOS_HOST: str | None = None
    HELIOS_PORT: int | None = None

    APP_HOST: str = "localhost"
    APP_PORT: int = 8000

    DB_HOST: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DATABASE: str | None = None

    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None

    @field_validator("SESSION_EXPIRE", mode="before")
    @classmethod
    def session_expire_minutes_to_seconds(cls, value: str | int | None) -> int:
        """Convert the session expiration value provided in minutes into seconds."""
        if value is None:
            raise ValueError("SESSION_EXPIRE environment variable is required")
        return 60 * int(value)

    @computed_field(return_type=str)
    def HELIOS_API(self) -> str:
        return f"http://{self.HELIOS_HOST}:{self.HELIOS_PORT}"

    @computed_field(return_type=str)
    def AUTH_API(self) -> str:
        return f"http://{self.AUTH_HOST}:{self.AUTH_PORT}"


settings = Config()
