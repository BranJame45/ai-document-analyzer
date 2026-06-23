import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    file_type = Column(String, nullable=False)
    pages = Column(Integer, default=0)
    language = Column(String, default="unknown")
    response_lang = Column(String, default="es")
    raw_text = Column(Text, default="")
    template = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    result = Column(JSON, default=dict)
    doc_type = Column(String, default="")
    summary = Column(Text, default="")
    status = Column(String, default="pending")
    error_msg = Column(String, nullable=True)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
