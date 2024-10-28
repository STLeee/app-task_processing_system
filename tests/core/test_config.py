import pytest
from unittest import mock
from app.core.config import Settings

def test_default_values():
    with mock.patch.dict('os.environ', {}, clear=True):
        settings = Settings()
        assert settings.app_env == "dev"
        assert settings.log_level == "debug"
        assert settings.log_file_path == "logs/app.log"

def test_overridden_values():
    env_vars = {
        "APP_ENV": "prod",
        "LOG_LEVEL": "info",
        "LOG_PATH": "/var/log/app.log",
        "DATABASE_URL": "postgresql://user:password@localhost/dbname",
        "REDIS_HOST": "redis-server"
    }
    with mock.patch.dict('os.environ', env_vars, clear=True):
        settings = Settings()
        assert settings.app_env == "prod"
        assert settings.log_level == "info"
        assert settings.log_file_path == "/var/log/app.log"
        assert settings.database_url == "postgresql://user:password@localhost/dbname"
        assert settings.redis_host == "redis-server"

def test_env_file_loading():
    env_vars = {
        "APP_ENV": "stag",
        "LOG_LEVEL": "warning",
        "LOG_PATH": "/tmp/app.log",
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_HOST": "127.0.0.1"
    }
    with mock.patch.dict('os.environ', env_vars, clear=True):
        settings = Settings(_env_file='.env')
        assert settings.app_env == "stag"
        assert settings.log_level == "warning"
        assert settings.log_file_path == "/tmp/app.log"
        assert settings.database_url == "sqlite:///test.db"
        assert settings.redis_host == "127.0.0.1"
