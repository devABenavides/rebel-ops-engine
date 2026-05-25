import os
from pathlib import Path

from dotenv import load_dotenv

_dotenv_loaded = False


def ensure_env_loaded():
    global _dotenv_loaded
    if not _dotenv_loaded:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        _dotenv_loaded = True


def get(key: str, default: str = "") -> str:
    ensure_env_loaded()
    return os.getenv(key, default)
