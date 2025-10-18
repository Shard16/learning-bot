from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    TELEGRAM_BOT_TOKEN: str = "8373204697:AAHXHtC84dXkfamlz2euguB6rX81wv_QzYg"

    class Config:
        env_file = ".env"

settings = Settings()
