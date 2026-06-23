import pytest
from io import BytesIO

from app.services.pdf_extractor import extract_text_from_pdf, build_system_prompt


class TestPDFExtractor:
    @pytest.mark.asyncio
    async def test_extract_invalid_pdf(self):
        with pytest.raises(ValueError, match="OCR processing failed"):
            await extract_text_from_pdf(b"invalid content")

    def test_build_system_prompt_generic(self):
        prompt = build_system_prompt(None, None, "es")
        assert "Spanish" in prompt
        assert "{text}" in prompt

    def test_build_system_prompt_cv(self):
        prompt = build_system_prompt("cv", None, "en")
        assert "CV/resume" in prompt
        assert "Full name" in prompt
        assert "English" in prompt

    def test_build_system_prompt_invoice(self):
        prompt = build_system_prompt("invoice", None, "es")
        assert "Invoice" in prompt
        assert "Spanish" in prompt

    def test_build_system_prompt_contract(self):
        prompt = build_system_prompt("contract", "Focus on dates", "en")
        assert "Contract" in prompt
        assert "Focus on dates" in prompt

    def test_build_system_prompt_custom_instructions(self):
        prompt = build_system_prompt(None, "Extract all numbers", "en")
        assert "Extract all numbers" in prompt
