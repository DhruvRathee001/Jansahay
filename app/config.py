import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    app_name: str = os.getenv("APP_NAME", "JanSahay")
    secret_key: str = os.getenv("SECRET_KEY", "local-development-secret-change-me")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'jansahay.db'}")
    upload_dir: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)

