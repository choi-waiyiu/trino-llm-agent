from pydantic import UUID4
from typing import Optional
from trino_llm_agent.domain.vector_document import VectorDocument

class EmbeddedChunk(VectorDocument):
    chunk_content: str
    embedding: list[float]
    document_id: UUID4
    software: str
    class VectorDBConfig:
        collection_name = "embedded_chunk"
        use_vector_index = True
