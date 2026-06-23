def get_prompt(lang: str) -> str:
    return f"""
You are a document analysis assistant. Analyze the following document text and provide:
- Document type
- Executive summary
- Key entities (people, dates, amounts, organizations)
- Main points

Respond in {"Spanish" if lang == "es" else "English"}.

Document text:
{{text}}
"""
