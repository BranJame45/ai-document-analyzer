import pytest

from app.services.llm_service import analyze_document, parse_llm_response, detect_language


class TestLLMService:
    def test_parse_llm_response_json(self):
        content = '{"key": "value"}'
        result = parse_llm_response(content)
        assert result == {"key": "value"}

    def test_parse_llm_response_markdown_json(self):
        content = '```json\n{"key": "value"}\n```'
        result = parse_llm_response(content)
        assert result == {"key": "value"}

    def test_parse_llm_response_invalid(self):
        content = "Some plain text response"
        result = parse_llm_response(content)
        assert result == {"raw_response": content}

    def test_detect_language_spanish(self):
        text = "El desarrollo de software es una profesión muy demandada en el mercado laboral."
        assert detect_language(text) == "es"

    def test_detect_language_english(self):
        text = "The development of software is a highly demanded profession in the labor market."
        assert detect_language(text) == "en"

    def test_detect_language_unknown(self):
        text = "1234567890 !@#$%^&*()"
        assert detect_language(text) == "unknown"
