from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import re
from trino_llm_agent.domain.documents import RawDocument
from trino_llm_agent.domain.cleaned_document import CleanedDocument, CleanedTrinoBlogPost, CleanedTrinoDocumentation, CleanedTrinoReleaseNote

RawDocumentT = TypeVar("RawDocumentT", bound=RawDocument)
CleanedDocumentT = TypeVar("CleanDocumentT", bound=CleanedDocument)

class DataCleaningHandler(ABC, Generic[RawDocumentT, CleanedDocumentT]):
    @abstractmethod
    def clean(self, raw_document: RawDocumentT) -> CleanedDocumentT:
        pass

    def _clean_content(self, content: str) -> str:
        cleaned_content = content
        cleaned_content = cleaned_content.encode('ascii', errors='ignore').decode('utf-8')
        cleaned_content = re.sub(r'\n{2,}', '\n', cleaned_content)
        cleaned_content = re.sub(r"\s+", " ", cleaned_content)
        cleaned_content = cleaned_content.strip()
        return cleaned_content

class TrinoBlogPostCleaningHandler(DataCleaningHandler):
    def clean(self, raw_document: RawDocument) -> CleanedTrinoBlogPost:
        cleaned_content = self._clean_content(raw_document.content)
        return CleanedTrinoBlogPost(
            content=cleaned_content,
            link=raw_document.link
        )

class TrinoDocumentationCleaningHandler(DataCleaningHandler):
    def clean(self, raw_document: RawDocument) -> CleanedTrinoDocumentation:
        cleaned_content = self._clean_content(raw_document.content)
        return CleanedTrinoDocumentation(
            content=cleaned_content,
            link=raw_document.link
        )

class TrinoReleaseNoteCleaningHandler(DataCleaningHandler):
    def clean(self, raw_document: RawDocument) -> CleanedTrinoReleaseNote:
        cleaned_contet = self._clean_content(raw_document.content)
        return CleanedTrinoReleaseNote(
            content=cleaned_contet,
            link=raw_document.link
        )
