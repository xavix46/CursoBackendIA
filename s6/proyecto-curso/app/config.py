from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite:///./gastos.db"
    access_token_expire_minutes: int = 30
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
