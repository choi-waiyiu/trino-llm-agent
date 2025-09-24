from functools import cached_property
from typing import Optional
from sentence_transformers.SentenceTransformer import SentenceTransformer
from trino_llm_agent.settings import settings

class EmbeddingModel:
    _instance: Optional["EmbeddingModel"] = None
    _model: Optional[SentenceTransformer] = None

    @classmethod
    def get_instance(cls) -> "EmbeddingModel":
        if cls._instance is None:
            cls._instance = cls()
            cls._model = SentenceTransformer(
                settings.EMBEDDING_MODEL_ID,
                device=settings.RAG_MODEL_DEVICE,
                cache_folder=None
                )
            cls._model.eval()
        return cls._instance
    
    @cached_property
    def embedding_size(self) -> int:
        return self._model.get_sentence_embedding_dimension()
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()
