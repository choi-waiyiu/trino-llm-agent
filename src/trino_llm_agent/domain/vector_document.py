import uuid
from uuid import UUID
from abc import ABC
from typing import Generic, TypeVar, Type, get_type_hints
from pydantic import UUID4, BaseModel, Field
from qdrant_client.models import PointStruct, Record, VectorParams, Distance
from qdrant_client.conversions.common_types import PointId
from trino_llm_agent.domain.db.qdrant import qdrant_client
from trino_llm_agent.applications.embedding.embedding_model import EmbeddingModel
from loguru import logger

T = TypeVar("T", bound="VectorDocument")

class VectorDocument(BaseModel, Generic[T], ABC):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    class VectorDBConfig:
        collection_name = "default"
        use_vector_index = False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    @classmethod
    def from_record(cls: Type[T], record: Record) -> T:
        attributes = {
            "id": UUID(record.id, version=4),
            **(record.payload or {})
        }
        if "embedding" in get_type_hints(cls):
            attributes["embedding"] = record.vector or None
        return cls(**attributes)
    
    @classmethod
    def from_records(cls: Type[T], records: list[Record]) -> list[T]:
        return [cls.from_record(record) for record in records]
    
    def to_point(self: T) -> PointStruct:
        payload = super().model_dump()
        _id = str(payload.pop("id", self.id))
        vector = payload.pop("embedding", {})
        payload["document_id"] = str(payload.pop("document_id", ""))
        return PointStruct(id=_id, vector=vector, payload=payload)
    
    @classmethod
    def batch_upsert(cls: Type[T], documents: list["VectorDocument"], batch_size:int = 10) -> None:
        points = [document.to_point() for document in documents]
        for batch in cls._batch_documents(points, batch_size):
            qdrant_client.upsert(collection_name=cls.get_collection_name(), points=batch)

    @classmethod
    def _batch_documents(cls: Type[T], documents: list["VectorDocument"], batch_size):
        for i in range(0, len(documents), batch_size):
            yield documents[i:i + batch_size]
    
    @classmethod
    def batch_find(cls: Type[T], limit: int = 10, offset: PointId = None) -> tuple[list[T], PointId | None]:
        records, next_offset = qdrant_client.scroll(
            collection_name=cls.get_collection_name(),
            limit=limit,
            offset=offset,
            with_vectors=cls.VectorDBConfig.use_vector_index
        )
        documents = cls.from_records(records)
        return documents, next_offset
    
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        collection_name = cls.VectorDBConfig.collection_name
        if qdrant_client.collection_exists(collection_name=collection_name):
            logger.info(collection_name + " exists")
            return collection_name
        if cls.VectorDBConfig.use_vector_index:
            vectors_config = VectorParams(size=EmbeddingModel.get_instance().embedding_size, distance=Distance.COSINE)
        else:
            vectors_config = {}
        logger.info("Create collection: " + collection_name)
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config
        )
        return collection_name
        
