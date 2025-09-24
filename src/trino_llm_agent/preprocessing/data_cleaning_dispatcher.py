from trino_llm_agent.domain.documents import DocumentType
from trino_llm_agent.domain.vector_document import VectorDocument
from trino_llm_agent.preprocessing.data_cleaning_handlers import *

class DataCleaningHandlerFactory:
    @staticmethod
    def create_handler(document_type: str) -> DataCleaningHandler:
        match document_type:
            case DocumentType.BLOG_POST.value:
                return TrinoBlogPostCleaningHandler()
            case DocumentType.DOCUMENTATION.value:
                return TrinoDocumentationCleaningHandler()
            case DocumentType.RELEASE_NOTE.value:
                return TrinoReleaseNoteCleaningHandler()
            case _:
                raise ValueError("Unspported document type")

class DataCleaningHnadlerDispatcher:
    factory = DataCleaningHandlerFactory()

    @classmethod
    def dispatch(cls, raw_document: RawDocument) -> VectorDocument:
        document_type = raw_document.document_type
        handler = cls.factory.create_handler(document_type)
        return handler.clean(raw_document)
