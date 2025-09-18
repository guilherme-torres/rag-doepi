from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = ".env"

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")
    
    GEMINI_API_KEY: str
    AI_MODEL: str
    SHEETS_URL: str
    DOEPI_ENDPOINT: str
    DOWNLOAD_DIR: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
