# Master Prompt — AI Document Analyzer (API de Análisis de Documentos)

> Copia y pega este prompt completo en una IA (Claude, Cursor, ChatGPT) para que genere el scaffold del proyecto.
> Este prompt es solo para crear la ESTRUCTURA y archivos base. No implementa la lógica completa — eso se hace fase por fase.

---

## PROMPT

Eres un arquitecto de software backend especializado en Python. Tu tarea es crear el scaffold completo de una API REST llamada AI Document Analyzer.

Lee atentamente todo lo que sigue antes de escribir cualquier archivo.

---

### CONTEXTO DEL PROYECTO

AI Document Analyzer es una API REST en Python con FastAPI que recibe documentos (PDFs e imágenes) y extrae información estructurada usando un LLM (Groq). Es un proyecto backend puro sin frontend — se documenta y consume con Swagger UI.

El sistema acepta cualquier tipo de documento, en español o inglés, de hasta 20 páginas. Tiene plantillas predefinidas para CVs, facturas y contratos, y también permite extracción libre con instrucciones del usuario.

**Stack:**
- Framework: FastAPI (Python 3.11+)
- Validación: Pydantic v2
- ORM: SQLAlchemy (async) + Alembic
- Base de datos: PostgreSQL
- LLM: Groq API
- PDF: PyPDF2 + pdfplumber
- OCR: Tesseract (pytesseract)
- Imágenes: Pillow
- Storage: Supabase Storage
- Contenedores: Docker + docker-compose
- Auth: API Key por header

---

### ESTRUCTURA DE ARCHIVOS QUE DEBES CREAR

```
ai-document-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── document.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── document.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── documents.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py
│   │   ├── ocr_service.py
│   │   ├── llm_service.py
│   │   ├── storage_service.py
│   │   └── export_service.py
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── generic.py
│   │   ├── cv.py
│   │   ├── invoice.py
│   │   └── contract.py
│   └── middleware/
│       ├── __init__.py
│       └── api_key.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pdf_extractor.py
│   ├── test_llm_service.py
│   └── test_endpoints.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── PROJECT_STRUCTURE.md
```

---

### INSTRUCCIONES DE IMPLEMENTACIÓN

**1. requirements.txt**
```
fastapi==0.111.0
uvicorn[standard]==0.30.0
pydantic==2.7.0
pydantic-settings==2.3.0
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
alembic==1.13.0
PyPDF2==3.0.1
pdfplumber==0.11.0
pytesseract==0.3.10
Pillow==10.3.0
httpx==0.27.0
python-multipart==0.0.9
openpyxl==3.1.2
supabase==2.4.0
python-dotenv==1.0.1
```

**2. app/config.py**
Usar `BaseSettings` de pydantic-settings:
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str = "documents"
    API_KEY: str
    MAX_PAGES: int = 20
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
```

**3. app/models/document.py**
Modelo SQLAlchemy para `DocumentAnalysis`:
- id (UUID, PK)
- filename (String)
- file_url (String, nullable)
- file_type (String: "pdf" | "image")
- pages (Integer)
- language (String: "es" | "en" | "unknown") — idioma detectado del documento
- response_lang (String: "es" | "en") — idioma en que respondió el LLM
- raw_text (Text) — texto extraído antes del LLM
- template (String, nullable: "cv" | "invoice" | "contract" | None)
- instructions (Text, nullable) — instrucciones personalizadas del usuario
- result (JSON) — resultado estructurado del LLM
- doc_type (String) — tipo de documento detectado por IA
- summary (Text) — resumen generado por IA
- status (String: "pending" | "processing" | "done" | "error")
- error_msg (String, nullable)
- duration_ms (Integer)
- created_at (DateTime)

**4. app/schemas/document.py**
Pydantic schemas:
- `AnalyzeRequest` — para el form data (template opcional, instructions opcional, lang opcional)
- `AnalyzeResponse` — respuesta completa del análisis
- `DocumentListItem` — para el listado paginado
- `DocumentDetail` — detalle completo de un análisis

**5. app/middleware/api_key.py**
Middleware o dependency que valida el header `X-API-Key`.
Si no coincide con `settings.API_KEY` → retorna 401.
Excluir `/health` y `/docs` y `/openapi.json`.

**6. app/services/pdf_extractor.py**
```python
async def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Extrae texto de un PDF.
    - Si tiene texto embebido: usa pdfplumber
    - Si es escaneado (sin texto): convierte a imagen y usa OCR
    - Retorna (texto_extraido, numero_de_paginas)
    - Lanza ValueError si supera MAX_PAGES
    """
    pass

async def is_scanned_pdf(file_bytes: bytes) -> bool:
    """Detecta si el PDF es escaneado (sin texto embebido)"""
    pass
```

**7. app/services/ocr_service.py**
```python
async def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Preprocesa la imagen con Pillow (escala de grises, contraste)
    y extrae texto con Tesseract.
    """
    pass
```

**8. app/services/llm_service.py**
```python
async def analyze_document(
    text: str,
    template: str | None,
    instructions: str | None,
    lang: str
) -> dict:
    """
    Llama a Groq API con el texto y las instrucciones.
    Retorna dict con: doc_type, summary, result (JSON estructurado), language_detected
    """
    pass

def build_system_prompt(template: str | None, instructions: str | None, lang: str) -> str:
    """
    Construye el system prompt según el template o instrucciones libres.
    Siempre instruye responder en el idioma indicado por lang.
    """
    pass
```

**9. app/templates/**
Cada archivo exporta una función `get_prompt(lang: str) -> str` con el system prompt específico:

- `cv.py` → extrae: nombre, email, teléfono, experiencia laboral (empresa, cargo, fechas, descripción), educación, skills
- `invoice.py` → extrae: número de factura, fecha, emisor (nombre, RUC/NIF), receptor, ítems (descripción, cantidad, precio), subtotal, impuestos, total
- `contract.py` → extrae: partes involucradas, objeto del contrato, fecha inicio, fecha fin, montos, cláusulas principales
- `generic.py` → análisis libre: tipo de documento, resumen, entidades clave, puntos principales

**10. app/routers/documents.py**
Endpoints:
```
POST   /api/analyze              → recibe archivo + opciones, procesa y guarda
GET    /api/documents            → lista paginada (query: page, limit, type, from_date, to_date)
GET    /api/documents/{id}       → detalle completo
DELETE /api/documents/{id}       → elimina análisis y archivo de storage
GET    /api/documents/{id}/export/json   → descarga JSON
GET    /api/documents/{id}/export/excel  → descarga Excel
GET    /api/templates            → lista plantillas disponibles
GET    /health                   → { status: "ok", version: "1.0.0" }
```

**11. app/main.py**
- Instanciar FastAPI con título, descripción y versión (para Swagger)
- Registrar el router de documents
- CORS abierto (para poder probar desde Swagger)
- Evento startup para verificar conexión a BD
- Endpoint `/health` sin autenticación

**12. docker-compose.yml**
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db]
    volumes:
      - .:/app
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: docanalyzer
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
volumes:
  postgres_data:
```

**13. Dockerfile**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

### VARIABLES DE ENTORNO

**.env.example:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/docanalyzer
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_BUCKET=documents
API_KEY=change_this_api_key
MAX_PAGES=20
MAX_FILE_SIZE_MB=10
```

---

### AL FINALIZAR — genera PROJECT_STRUCTURE.md

Una vez creados todos los archivos, genera un archivo `PROJECT_STRUCTURE.md` en la raíz con:

1. **Mapa de archivos** — árbol completo con descripción de cada archivo
2. **Pipeline de procesamiento** — flujo completo desde que llega el archivo hasta que se guarda el resultado
3. **Cómo funciona la autenticación** — API Key, qué endpoints la requieren
4. **Cómo funciona cada template** — diferencia entre CV, factura, contrato y genérico
5. **Cómo agregar un template nuevo** — pasos exactos
6. **Cómo probar la API** — ejemplos de curl para cada endpoint
7. **Cómo correr con Docker** — comandos paso a paso
8. **Cómo hacer deploy en Render** — pasos y configuración
