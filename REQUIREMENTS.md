# AI Document Analyzer — API de Análisis de Documentos con IA

## Contexto General

AI Document Analyzer es una API REST construida en Python con FastAPI que recibe documentos (PDFs e imágenes) y extrae información estructurada usando un LLM. El propósito principal es demostrar conocimiento técnico en FastAPI, procesamiento de documentos y consumo de APIs de IA.

Este proyecto es intencionalmetne un **backend puro sin frontend** — se consume mediante Postman, Bruno u otro cliente HTTP. Es el proyecto más técnico del portafolio y está pensado para mostrar conocimientos en Python moderno, arquitectura de APIs asíncronas y cadenas de procesamiento LLM.

El sistema acepta cualquier tipo de documento, en español o inglés, de hasta 20 páginas. El usuario define qué información quiere extraer.

---

## Decisiones de Arquitectura

- **Sin frontend** — API pura, documentada con Swagger/OpenAPI automático de FastAPI
- **Sin autenticación compleja** — API Key simple por header para proteger los endpoints
- **Procesamiento asíncrono** para documentos grandes
- **Agnóstico al tipo de documento** — el usuario indica qué extraer
- **Límite:** 20 páginas por documento

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Framework | **FastAPI** (Python 3.11+) |
| Validación | **Pydantic v2** |
| ORM | **SQLAlchemy** (async) con Alembic para migraciones |
| Base de datos | PostgreSQL (Supabase) |
| LLM | **Groq API** (llama-3.3-70b-versatile) |
| PDF parsing | **PyPDF2** + **pdfplumber** |
| OCR (imágenes) | **Tesseract** vía pytesseract |
| Preprocesamiento imagen | **Pillow** |
| Storage de archivos | **Supabase Storage** |
| Tareas async | **Celery** + Redis (para documentos grandes) |
| Contenedores | **Docker** + docker-compose |
| Docs automáticas | Swagger UI (incluido en FastAPI en /docs) |
| Hosting | Render |

---

## Funcionalidades

### 1. Subida y procesamiento de documentos

**Tipos de input aceptados:**
- PDF (texto embebido o escaneado)
- Imágenes: JPG, PNG, WEBP (foto de un documento)
- Límite: 20 páginas / 10 MB por archivo
- Campo opcional `lang`: `"es"` | `"en"` — el LLM responde en ese idioma. Si no se especifica, el sistema detecta el idioma del documento automáticamente.

**Pipeline de procesamiento:**
```
Archivo recibido
    │
    ├── Si es PDF con texto → extraer texto directamente (PyPDF2/pdfplumber)
    ├── Si es PDF escaneado → convertir páginas a imagen → OCR (Tesseract)
    └── Si es imagen → OCR (Tesseract) + preprocesamiento (Pillow)
    │
    ▼
Texto extraído y limpiado
    │
    ▼
Enviar a LLM (Groq) con instrucciones de extracción
    │
    ▼
JSON estructurado como respuesta
```

### 2. Extracción inteligente

El usuario puede:

**a) Extracción genérica:** El LLM analiza el documento libremente y devuelve:
- Tipo de documento detectado
- Resumen ejecutivo
- Entidades clave (personas, fechas, montos, organizaciones)
- Puntos principales

**b) Extracción dirigida:** El usuario envía instrucciones específicas:
```json
{
  "instructions": "Extrae: nombre del empleado, empresa, sueldo mensual, fecha de inicio"
}
```
El LLM extrae exactamente eso y lo devuelve en JSON estructurado.

**c) Extracción por plantilla predefinida:**
El sistema incluye plantillas listas para tipos comunes:
- `cv` → nombre, email, teléfono, experiencia, educación, skills
- `invoice` → número de factura, fecha, emisor, receptor, ítems, total, impuestos
- `contract` → partes involucradas, objeto del contrato, fechas, cláusulas clave, montos

### 3. Persistencia

Cada análisis se guarda en la base de datos:
- Archivo original en Supabase Storage
- Texto extraído
- Resultado del análisis en JSON
- Metadatos: tipo, páginas, idioma detectado, fecha, duración del procesamiento

### 4. Historial y búsqueda

- Listar todos los documentos analizados (con paginación)
- Ver el detalle de un análisis anterior
- Buscar por tipo de documento o rango de fechas
- Eliminar un análisis y su archivo

### 5. Exportación

- Exportar resultado a JSON (directo desde la API)
- Exportar resultado a Excel (una fila por documento, columnas dinámicas según los campos extraídos)

---

## Modelo de Datos (SQLAlchemy)

```python
class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id           = Column(UUID, primary_key=True, default=uuid4)
    filename     = Column(String, nullable=False)
    file_url     = Column(String)               # URL en Supabase Storage
    file_type    = Column(String)               # pdf | image
    pages        = Column(Integer)
    language     = Column(String)               # es | en | unknown (idioma detectado del documento)
    response_lang = Column(String)              # es | en (idioma en que respondió el LLM)
    raw_text     = Column(Text)                 # texto extraído antes de IA
    template     = Column(String, nullable=True) # cv | invoice | contract | None
    instructions = Column(Text, nullable=True)  # instrucciones personalizadas
    result       = Column(JSONB)                # resultado estructurado del LLM
    doc_type     = Column(String)               # tipo detectado por IA
    summary      = Column(Text)                 # resumen generado por IA
    status       = Column(String)               # pending | processing | done | error
    error_msg    = Column(String, nullable=True)
    duration_ms  = Column(Integer)              # tiempo de procesamiento
    created_at   = Column(DateTime, default=datetime.utcnow)
```

---

## Endpoints API

```
POST   /api/analyze
       Body: multipart/form-data
       - file: archivo PDF o imagen
       - template: "cv" | "invoice" | "contract" | null (opcional)
       - instructions: string (opcional, para extracción dirigida)
       Response: { id, status, result, summary, doc_type, pages, duration_ms }

GET    /api/documents
       Query: page, limit, type, from_date, to_date
       Response: lista paginada de análisis

GET    /api/documents/:id
       Response: análisis completo con resultado JSON

DELETE /api/documents/:id
       Response: 204 No Content

GET    /api/documents/:id/export/json
       Response: archivo JSON descargable

GET    /api/documents/:id/export/excel
       Response: archivo Excel descargable

GET    /api/templates
       Response: lista de plantillas disponibles con descripción

GET    /health
       Response: { status: "ok", version, uptime }
```

**Autenticación:** Header `X-API-Key: your_api_key` en todos los endpoints excepto `/health`.

---

## Estructura de Carpetas

```
ai-document-analyzer/
├── app/
│   ├── main.py                 (FastAPI app, routers, CORS)
│   ├── config.py               (Settings con Pydantic BaseSettings)
│   ├── database.py             (SQLAlchemy async engine)
│   ├── models/
│   │   └── document.py         (SQLAlchemy models)
│   ├── schemas/
│   │   └── document.py         (Pydantic schemas request/response)
│   ├── routers/
│   │   └── documents.py        (endpoints)
│   ├── services/
│   │   ├── pdf_extractor.py    (PyPDF2 + pdfplumber)
│   │   ├── ocr_service.py      (Tesseract)
│   │   ├── llm_service.py      (Groq API)
│   │   ├── storage_service.py  (Supabase Storage)
│   │   └── export_service.py   (JSON + Excel)
│   ├── templates/
│   │   ├── cv.py               (prompt template para CVs)
│   │   ├── invoice.py          (prompt template para facturas)
│   │   └── contract.py         (prompt template para contratos)
│   └── middleware/
│       └── api_key.py          (validación del API Key)
├── alembic/                    (migraciones de BD)
├── tests/
│   ├── test_pdf_extractor.py
│   ├── test_llm_service.py
│   └── test_endpoints.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Variables de Entorno

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/docanalyzer
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=documents
API_KEY=your_secret_api_key
MAX_PAGES=20
MAX_FILE_SIZE_MB=10
```

---

## Docker Compose

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db]

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

---

## Fases de Desarrollo

### Fase 1: Setup + Estructura base (Día 1-2)
- Inicializar FastAPI con estructura de carpetas
- Configurar SQLAlchemy async + Alembic
- Conectar PostgreSQL
- Middleware de API Key
- Endpoint `/health` funcional
- Docker + docker-compose

### Fase 2: Extracción de texto (Día 3-4)
- Servicio PDF (texto embebido)
- Servicio OCR (imágenes y PDFs escaneados)
- Preprocesamiento de imágenes con Pillow
- Tests unitarios para extractores

### Fase 3: Integración LLM (Día 5-6)
- Servicio Groq con manejo de errores y reintentos
- Plantillas de prompts (genérico, CV, factura, contrato)
- Extracción dirigida por instrucciones del usuario
- Parseo y validación del JSON devuelto por el LLM

### Fase 4: Persistencia + Storage (Día 7)
- Guardar análisis en PostgreSQL
- Subir archivos a Supabase Storage
- Endpoints GET (listar, detalle, eliminar)

### Fase 5: Exportación + Docs (Día 8-9)
- Exportar a JSON y Excel
- Revisar y mejorar documentación Swagger automática
- Tests de integración para endpoints principales

### Fase 6: Deploy (Día 10)
- Deploy en Render
- Variables de entorno configuradas
- README con ejemplos de uso con curl/Postman
- Screenshots de Swagger UI para el portafolio

---

## Criterios de Éxito

- La API extrae información correctamente de PDFs de texto
- La API extrae información de imágenes vía OCR (aunque con menor precisión)
- Las plantillas predefinidas (CV, factura, contrato) devuelven JSON estructurado coherente
- La documentación Swagger está completa y permite probar todos los endpoints
- La app corre con docker-compose en un solo comando
- Está desplegada en Render y accesible públicamente
