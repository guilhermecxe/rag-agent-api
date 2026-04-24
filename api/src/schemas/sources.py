from pydantic import BaseModel
from typing import Any


class DocumentModel(BaseModel):
    page_content: str
    metadata: dict[str, Any]


class StatusResponse(BaseModel):
    status: str


class SourcesPage(BaseModel):
    sources: list[str]
    current_page: int
    last_page: int

# ---

class GetSourcesResponse(BaseModel):
    sources: SourcesPage


class SearchSourcesRegexResponse(BaseModel):
    sources: list[str]
    current_page: int
    last_page: int


class GetExcerptResponse(BaseModel):
    excerpt: DocumentModel


class SearchExcerptsRegexResponse(BaseModel):
    excerpts: list[DocumentModel]
    current_page: int
    last_page: int


class SearchExcerptsSemanticResponse(BaseModel):
    excerpts: list[DocumentModel]


class SearchDocumentsResponse(BaseModel):
    documents: list[DocumentModel]
