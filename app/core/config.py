from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://user:password@db:5432/app"
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    FACE_IMAGE_UPLOAD_DIR: str = "app/images/uploads"
    FACE_MATCH_TOLERANCE: float = 0.48

settings = Settings()
