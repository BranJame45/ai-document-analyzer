from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    template: str | None = Field(None, description="Template name: cv, invoice, contract")
    instructions: str | None = Field(None, description="Custom extraction instructions")
    lang: str = Field("es", description="Response language: es or en")


class AnalyzeResponse(BaseModel):
    id: UUID
    status: str
    filename: str
    file_type: str
    pages: int
    language: str
    response_lang: str
    doc_type: str
    summary: str
    result: dict
    duration_ms: int
    created_at: datetime


class DocumentListItem(BaseModel):
    id: UUID
    filename: str
    file_type: str
    pages: int
    doc_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(BaseModel):
    id: UUID
    filename: str
    file_url: str | None
    file_type: str
    pages: int
    language: str
    response_lang: str
    raw_text: str
    template: str | None
    instructions: str | None
    result: dict
    doc_type: str
    summary: str
    status: str
    error_msg: str | None
    duration_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list[DocumentListItem]
    total: int
    page: int
    limit: int
    pages: int
