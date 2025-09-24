from abc import ABC
from trino_llm_agent.domain.documents import DocumentType
from trino_llm_agent.domain.vector_document import VectorDocument

class CleanedDocument(VectorDocument, ABC):
    software_name: str
    content: str
    link: str

'''
The cleaned document is stored to vector db without embedding so disable use_vector_index to save memory
'''
class CleanedTrinoDocument(CleanedDocument):
    software_name: str = "Trino"

class CleanedTrinoBlogPost(CleanedTrinoDocument):
    class VectorDBConfig:
        collection_name = "cleaned_blog_post"
        use_vector_index = False
    class DocumentType:
        type = DocumentType.BLOG_POST

class CleanedTrinoReleaseNote(CleanedTrinoDocument):
    class VectorDBConfig:
        collection_name = "cleaned_release_node"
        use_vector_index = False
    class DocumentType:
        type = DocumentType.RELEASE_NOTE

class CleanedTrinoDocumentation(CleanedTrinoDocument):
    class VectorDBConfig:
        collection_name = "cleaned_documentation"
        use_vector_index = False
    class DocumentType:
        type = DocumentType.DOCUMENTATION
