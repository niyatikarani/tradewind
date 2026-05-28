from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str = "change-me-in-production-use-a-long-random-string"
    session_max_age: int = 86400  # 24 hours
    database_path: str = "quotation.db"
    fx_api_key: str = ""
    debug: bool = False


settings = Settings()
