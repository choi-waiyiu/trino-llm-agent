from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    DATABASE_HOST: str = "mongodb://trino_llm_agent:tmp@127.0.0.1"
    DATABASE_PORT: int = 27017
    DATABASE_NAME: str = "trino_llm_agent"

    # Qdrant vector database
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # RAG
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_MODEL_DEVICE: str = "cpu"

    @classmethod
    def load_settings(cls) -> "Settings": #Forward Reference
        # TODO: load from ZenML or .env
        return Settings()

settings = Settings.load_settings()
