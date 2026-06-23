import io

from app.config import settings
from app.templates import generic, cv, invoice, contract


async def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    max_pages = settings.MAX_PAGES

    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = len(pdf.pages)
            if pages > max_pages:
                raise ValueError(f"Document exceeds maximum of {max_pages} pages")

            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

            if text.strip():
                return text.strip(), pages

    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages = len(reader.pages)
        if pages > max_pages:
            raise ValueError(f"Document exceeds maximum of {max_pages} pages")

        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

        if text.strip():
            return text.strip(), pages
    except Exception:
        pass

    text = await extract_text_from_image(file_bytes)
    return text, 1


async def is_scanned_pdf(file_bytes: bytes) -> bool:
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:3]:
                text = page.extract_text() or ""
                if text.strip():
                    return False
        return True
    except Exception:
        return False


async def extract_text_from_image(file_bytes: bytes) -> str:
    try:
        from PIL import Image, ImageEnhance

        image = Image.open(io.BytesIO(file_bytes))
        image = image.convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)

        import pytesseract

        text = pytesseract.image_to_string(image, lang="spa+eng")
        return text.strip()
    except Exception as e:
        raise ValueError(f"OCR processing failed: {str(e)}")


def build_system_prompt(template: str | None, instructions: str | None, lang: str) -> str:
    if template == "cv":
        prompt = cv.get_prompt(lang)
    elif template == "invoice":
        prompt = invoice.get_prompt(lang)
    elif template == "contract":
        prompt = contract.get_prompt(lang)
    else:
        prompt = generic.get_prompt(lang)

    if instructions:
        prompt += f"\n\nAdditional user instructions:\n{instructions}\n"

    return prompt
