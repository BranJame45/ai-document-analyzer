import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db
from app.main import app
from app.config import settings
from app.models.document import DocumentAnalysis

TEST_DATABASE_URL = settings.DATABASE_URL

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def api_key_headers():
    return {"X-API-Key": settings.API_KEY}


@pytest_asyncio.fixture
async def sample_document():
    return DocumentAnalysis(
        filename="test.pdf",
        file_type="pdf",
        file_url="https://test.com/test.pdf",
        pages=2,
        language="es",
        raw_text="Sample text for testing",
        result={"key": "value"},
        doc_type="test",
        summary="Test summary",
        status="done",
        duration_ms=100,
    )
