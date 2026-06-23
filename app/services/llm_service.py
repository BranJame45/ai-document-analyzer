import json
import time

import httpx

from app.config import settings
from app.services.pdf_extractor import build_system_prompt


async def analyze_document(
    text: str,
    template: str | None,
    instructions: str | None,
    lang: str,
) -> dict:
    start = time.time()
    system_prompt = build_system_prompt(template, instructions, lang)
    user_prompt = system_prompt.replace("{text}", text)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a document analysis assistant. Extract structured data from the provided text."},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            structured = parse_llm_response(content)
            duration = int((time.time() - start) * 1000)

            return {
                "doc_type": structured.get("doc_type", template or "unknown"),
                "summary": structured.get("summary", ""),
                "structured_data": structured,
                "language_detected": detect_language(text),
                "response_lang": lang,
                "duration_ms": duration,
            }

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        return {
            "doc_type": "unknown",
            "summary": f"Analysis failed: {str(e)}",
            "structured_data": {"error": str(e)},
            "language_detected": "unknown",
            "response_lang": lang,
            "duration_ms": duration,
        }


def parse_llm_response(content: str) -> dict:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw_response": content}


def detect_language(text: str) -> str:
    spanish_keywords = ["el", "la", "los", "las", "de", "del", "para", "por", "con", "una", "que", "es", "en", "se", "su"]
    english_keywords = ["the", "is", "are", "of", "to", "in", "for", "on", "with", "this", "that", "from", "and", "or"]

    words = text.lower().split()
    es_count = sum(1 for w in words if w in spanish_keywords)
    en_count = sum(1 for w in words if w in english_keywords)

    if es_count > en_count:
        return "es"
    elif en_count > es_count:
        return "en"
    return "unknown"
