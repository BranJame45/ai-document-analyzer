import io

from PIL import Image, ImageEnhance


async def extract_text_from_image(file_bytes: bytes) -> str:
    try:
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
