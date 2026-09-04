from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "development"
    secret_key: str = "dev-only-insecure-key"
    fernet_key: str = ""

    database_url: str = "postgresql+asyncpg://drashti:drashti_dev_password@localhost:5432/drashti"
    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "drashti"
    minio_secret_key: str = "drashti_dev_password"
    minio_bucket: str = "drashti-evidence"
    minio_secure: bool = False

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    drashti_demo_mode: bool = True

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
