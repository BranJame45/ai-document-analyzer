from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.document import (
    AnalyzeRequest,
    AnalyzeResponse,
    DocumentListItem,
    DocumentDetail,
    PaginatedResponse,
)
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ocr_service import extract_text_from_image
from app.services.llm_service import analyze_document
from app.services.storage_service import upload_file
from app.services.export_service import export_json, export_excel
from app.middleware.api_key import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

TEMPLATES = {
    "cv": "Extract structured data from a CV/resume",
    "invoice": "Extract structured data from an invoice",
    "contract": "Extract structured data from a contract",
}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...),
    template: str = Form(None),
    instructions: str = Form(None),
    lang: str = Form("es"),
    db: AsyncSession = Depends(get_db),
):
    file_bytes = await file.read()
    file_type = "pdf" if file.filename.endswith(".pdf") else "image"

    if file_type == "pdf":
        raw_text, pages = await extract_text_from_pdf(file_bytes)
    else:
        raw_text = await extract_text_from_image(file_bytes)
        pages = 1

    result = await analyze_document(raw_text, template, instructions, lang)

    file_url = await upload_file(file_bytes, file.filename)

    from app.models.document import DocumentAnalysis

    analysis = DocumentAnalysis(
        filename=file.filename,
        file_url=file_url,
        file_type=file_type,
        pages=pages,
        language=result.get("language_detected", "unknown"),
        response_lang=result.get("response_lang", lang),
        raw_text=raw_text,
        template=template,
        instructions=instructions,
        result=result.get("structured_data", {}),
        doc_type=result.get("doc_type", ""),
        summary=result.get("summary", ""),
        status="done",
        duration_ms=result.get("duration_ms", 0),
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return analysis


@router.get("/documents", response_model=PaginatedResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    doc_type: str = Query(None, alias="type"),
    from_date: str = Query(None),
    to_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func
    from app.models.document import DocumentAnalysis

    query = select(DocumentAnalysis).order_by(DocumentAnalysis.created_at.desc())

    if doc_type:
        query = query.where(DocumentAnalysis.doc_type == doc_type)
    if from_date:
        query = query.where(DocumentAnalysis.created_at >= from_date)
    if to_date:
        query = query.where(DocumentAnalysis.created_at <= to_date)

    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=[DocumentListItem.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit if total > 0 else 0,
    )


@router.get("/documents/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.document import DocumentAnalysis

    result = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.document import DocumentAnalysis

    result = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(doc)
    await db.commit()


@router.get("/documents/{doc_id}/export/json")
async def export_document_json(doc_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.document import DocumentAnalysis

    result = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from fastapi.responses import Response
    json_bytes = export_json(doc)
    return Response(content=json_bytes, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="{doc.filename}_analysis.json"'})


@router.get("/documents/{doc_id}/export/excel")
async def export_document_excel(doc_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.document import DocumentAnalysis

    result = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from fastapi.responses import Response
    excel_bytes = export_excel(doc)
    return Response(content=excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{doc.filename}_analysis.xlsx"'})


@router.get("/templates")
async def list_templates():
    return [
        {"id": "cv", "name": "CV / Resume", "description": "Extracts personal info, experience, education, skills"},
        {"id": "invoice", "name": "Invoice", "description": "Extracts invoice number, dates, items, totals"},
        {"id": "contract", "name": "Contract", "description": "Extracts parties, dates, clauses, amounts"},
    ]
