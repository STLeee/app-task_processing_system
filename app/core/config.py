from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # app
    app_env: str = Field("dev", env="APP_ENV")
    log_level: str = Field("debug", env="LOG_LEVEL")
    log_file_path: str = Field(os.path.join("logs", "app.log"), env="LOG_FILE_PATH")

    # database
    database_url: str = Field("postgresql+asyncpg://username:password@localhost:5432/db", env="DATABASE_URL")

    # queue
    redis_host: str = Field("localhost", env="REDIS_HOST")

    def __init__(self, _env_file: str = None):
        if _env_file:
            self.Config.env_file = _env_file
        super().__init__()

    class Config:
        env_file_encoding = "utf-8"

settings = Settings(_env_file=f".env.{os.getenv('APP_ENV', 'dev')}")
