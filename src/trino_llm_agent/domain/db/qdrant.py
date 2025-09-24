from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from trino_llm_agent.settings import settings
from loguru import logger

class QdrantConnector:
    _client: QdrantClient | None = None

    def __new__(cls, *arg, **kwargs) -> QdrantClient:
        host = settings.QDRANT_DATABASE_HOST
        port = settings.QDRANT_DATABASE_PORT
        try:
            cls._client = QdrantClient(host=host, port=port)
            logger.info(f"Established connection to Qdrant: {host}:{port}")
        except UnexpectedResponse:
            logger.exception("Qdrant connection failed", host=host, port=port)
        return cls._client

qdrant_client = QdrantConnector()
