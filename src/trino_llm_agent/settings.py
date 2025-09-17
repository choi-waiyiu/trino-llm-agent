from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    DATABASE_HOST: str = "mongodb://trino_llm_agent:tmp@127.0.0.1"
    DATABASE_PORT: int = 27017
    DATABASE_NAME: str = "trino_llm_agent"

    @classmethod
    def load_settings(cls) -> "Settings": #Forward Reference
        # TODO: load from ZenML or .env
        return Settings()

settings = Settings.load_settings()
