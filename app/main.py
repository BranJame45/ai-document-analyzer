import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers.documents import router as documents_router
from app.middleware.api_key import APIKeyMiddleware

app = FastAPI(
    title="AI Document Analyzer API",
    description="Document analysis powered by AI (Groq) - extract structured data from PDFs and images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api/v1", tags=["documents"])


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "environment": os.getenv("ENVIRONMENT", "development")}
