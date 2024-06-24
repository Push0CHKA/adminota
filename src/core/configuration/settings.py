from functools import cache
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, conint
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """The settings for real sys / docker environment
    it is not for dotenv..."""

    name: str = ".env"
    ignore: bool = False

    @property
    def is_env_path_abs(self):
        return Path(self.name).is_absolute()


class LogSettings(BaseSettings):
    """Log settings"""

    model_config = SettingsConfigDict(env_prefix="log_")

    level: str = Field(
        default="INFO",
        description="Logging level",
    )
    path: str = Field(
        default="./",
        description="Log files absolute path",
    )
    name: str = Field(
        default="app.log",
        description="Log file name",
    )
    count: int = Field(
        default=10,
        description="Max log files count",
    )
    size: int = Field(
        default=1024 * 1024 * 2,
        description="Max log file size (bytes)",
    )


class DBSettings(BaseSettings):
    """Database settings"""

    model_config = SettingsConfigDict(env_prefix="db_")

    host: str = Field(
        default="database",
        description="Database host",
    )
    port: int = Field(
        default=5432,
        description="Database port",
    )
    user: str = Field(
        default="user",
        description="Database user",
    )
    password: str = Field(
        default="password",
        description="Database password",
    )
    name: str = Field(
        default="name",
        description="Database name",
    )


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="server_")

    workers: int = Field(
        default=1,
        description="Workers count",
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host ip address",
    )
    port: conint(gt=0, lt=2**16) = 5000
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @property
    def uvicorn_kwargs(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "log_level": self.log_level.lower(),
        }


class Settings(BaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    @property
    def uvicorn_kwargs(self) -> dict:
        return self.server.uvicorn_kwargs


@cache
def get_settings() -> Settings:
    if (env_settings := EnvSettings()).ignore:
        dotenv_path = None
    elif env_settings.is_env_path_abs:
        dotenv_path = env_settings.name
    else:
        dotenv_path = find_dotenv(env_settings.name)
    load_dotenv(dotenv_path)
    return Settings()
