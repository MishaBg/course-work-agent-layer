from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "course-work-agent-layer"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "video_agent"
    postgres_user: str = "video_agent"
    postgres_password: str = "video_agent"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "video-fragments"
    minio_secure: bool = False

    transport_service_url: str = "http://localhost:8080"
    transport_send_path: str = "/send"

    producer_stub_enabled: bool = True

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
