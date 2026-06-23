.
├── alembic.ini                           # Alembic configuration
├── alembic/                              # Database migrations
│   ├── env.py                            # Migration environment
│   ├── script.py.mako                    # Migration script template
│   └── versions/                         # Migration versions
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app entry point
│   ├── config.py                         # Settings via pydantic-settings
│   ├── database.py                       # SQLAlchemy async engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   └── document.py                   # DocumentAnalysis ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── document.py                   # Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── documents.py                  # API endpoints for /api/v1
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── api_key.py                    # API Key authentication
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py              # PDF text extraction (pdfplumber / PyPDF2)
│   │   ├── ocr_service.py                # OCR via pytesseract
│   │   ├── llm_service.py               # Groq LLM analysis
│   │   ├── storage_service.py            # Supabase Storage upload
│   │   └── export_service.py             # JSON / Excel export
│   └── templates/
│       ├── __init__.py
│       ├── generic.py                    # Generic analysis prompt
│       ├── cv.py                         # CV/resume analysis prompt
│       ├── invoice.py                    # Invoice analysis prompt
│       └── contract.py                   # Contract analysis prompt
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # Fixtures + test DB setup
│   ├── test_pdf_extractor.py             # PDF extractor unit tests
│   ├── test_llm_service.py              # LLM service unit tests
│   └── test_endpoints.py                 # API integration tests
├── Dockerfile                            # Python 3.11 with tesseract-ocr
├── docker-compose.yml                    # API + PostgreSQL services
├── requirements.txt                      # Python dependencies
├── runtime.txt                           # Python version
└── .env.example                          # Environment variables template
