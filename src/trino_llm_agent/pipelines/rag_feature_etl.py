from zenml import pipeline, step, get_step_context
from typing_extensions import Annotated
from trino_llm_agent.domain.documents import RawDocument
from trino_llm_agent.domain.vector_document import VectorDocument
from trino_llm_agent.preprocessing.data_cleaning_dispatcher import DataCleaningHnadlerDispatcher
from nltk import sent_tokenize
import nltk
from trino_llm_agent.applications.embedding.embedding_model import EmbeddingModel
from trino_llm_agent.domain.embedded_chuck import EmbeddedChunk
from loguru import logger

@pipeline()
def rag_feature_etl(software_names: list[str]) -> list[str]:
    raw_documents = get_raw_documents(software_names)
    cleaned_documents = clean_documents(raw_documents)
    embedded_chunks = embed_documents(cleaned_documents)
    last_step = insert_to_vector_db(embedded_chunks)
    return last_step.invocation_id



@step
def get_raw_documents(software_names: list[str]) -> Annotated[list[RawDocument], "raw_documents"]:
    raw_documents: list[RawDocument] = []
    for software_name in software_names:
        documents = list(RawDocument.objects(software__name__iregex=software_name))
        raw_documents.extend(documents)
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="raw_documents", metadata={"num_documents": len(raw_documents)})
    return raw_documents

@step
def clean_documents(documents: Annotated[list[RawDocument], "raw_documents"]) -> Annotated[list, "cleaned_documents"]:
    cleaned_documents = []
    for document in documents:
        cleaned_document = DataCleaningHnadlerDispatcher.dispatch(document)
        cleaned_documents.append(cleaned_document)
    return cleaned_documents

@step
def embed_documents(documents: Annotated[list[VectorDocument], "cleaned_documents"]) -> Annotated[list, "embedded_document"]:
    nltk.download('punkt_tab')
    embedding_model = EmbeddingModel.get_instance()
    embedded_chunks = []
    for document in documents:
        sentences = sent_tokenize(document.to_point().payload["content"])
        for i in range(0, len(sentences), 10):
            sentences_batch = sentences[i:i + 10]
            embedding_batch = embedding_model.embed(sentences_batch)
            for i in range(len(sentences_batch)):
                embedded_chunk = EmbeddedChunk(
                    chunk_content=sentences_batch[i],
                    embedding=embedding_batch[i],
                    document_id=document.id,
                    software="Trino"
                )
                embedded_chunks.append(embedded_chunk)
    return embedded_chunks

@step
def insert_to_vector_db(embedded_chunks: Annotated[list, "embedded_chunks"]) -> Annotated[bool, "successful"]:
    try:
        EmbeddedChunk.batch_upsert(embedded_chunks)
    except Exception as e:
        logger.error(f"{e!s}")
        return False
    return True
