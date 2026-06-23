import json
import io

from openpyxl import Workbook


def export_json(doc) -> bytes:
    data = {
        "id": str(doc.id),
        "filename": doc.filename,
        "file_type": doc.file_type,
        "pages": doc.pages,
        "language": doc.language,
        "response_lang": doc.response_lang,
        "template": doc.template,
        "instructions": doc.instructions,
        "doc_type": doc.doc_type,
        "summary": doc.summary,
        "result": doc.result,
        "duration_ms": doc.duration_ms,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def export_excel(doc) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Analysis"

    ws.append(["Field", "Value"])
    ws.append(["ID", str(doc.id)])
    ws.append(["Filename", doc.filename])
    ws.append(["Type", doc.file_type])
    ws.append(["Pages", doc.pages])
    ws.append(["Language", doc.language])
    ws.append(["Template", doc.template or ""])
    ws.append(["Doc Type", doc.doc_type])
    ws.append(["Summary", doc.summary or ""])
    ws.append(["Duration (ms)", doc.duration_ms])
    ws.append(["Created", doc.created_at.isoformat() if doc.created_at else ""])

    ws.append([])
    ws.append(["Extracted Data"])
    if doc.result:
        for key, value in doc.result.items():
            if isinstance(value, list):
                ws.append([key, json.dumps(value, ensure_ascii=False)])
            else:
                ws.append([key, value])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
