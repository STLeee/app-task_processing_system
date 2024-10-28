from pydantic import BaseSettings, Field
import os

class Settings(BaseSettings):
    # app
    app_env: str = Field("dev", env="APP_ENV")
    log_level: str = Field("debug", env="LOG_LEVEL")
    log_file_path: str = Field(os.path.join("logs", "app.log"), env="LOG_PATH")

    # database
    database_url: str = Field(..., env="DATABASE_URL")

    # queue
    redis_host: str = Field(..., env="REDIS_HOST")

    # auto load .env file
    class Config:
        env_file = f".env.{os.getenv('APP_ENV', 'dev')}"
        env_file_encoding = "utf-8"

settings = Settings()
