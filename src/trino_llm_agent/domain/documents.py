from mongoengine import *
from enum import Enum
import uuid

class DocumentType(Enum):
    BLOG_POST = "blog_post"
    RELEASE_NOTE = "release_note"
    DOCUMENTATION = "documentation"
    WEBPAGE = "webpage"

class Software(EmbeddedDocument):
    name = StringField(max_length=100, required=True)

class RawDocument(Document):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    software = EmbeddedDocumentField(Software)
    document_type = StringField(choices=[e.value for e in DocumentType], required=True)
    link = StringField(required=True)
    content = StringField(required=True)
    meta = {
        "allow_inheritance": True,
        "collection": "raw_document"
    }

class BlogPost(RawDocument):
    document_type = StringField(choices=[e.value for e in DocumentType], default=DocumentType.BLOG_POST.value, required=True)

class ReleaseNote(RawDocument):
    document_type = StringField(choices=[e.value for e in DocumentType], default=DocumentType.RELEASE_NOTE.value, required=True)

class Documentation(RawDocument):
    document_type = StringField(choices=[e.value for e in DocumentType], default=DocumentType.DOCUMENTATION.value, required=True)
