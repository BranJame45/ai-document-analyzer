def get_prompt(lang: str) -> str:
    return f"""
You are a CV/resume analysis assistant. Extract the following information from the CV text:

- Full name
- Email
- Phone
- Work experience (for each: company, position, dates, description)
- Education (for each: institution, degree, dates)
- Skills (list)
- Languages

Respond in {"Spanish" if lang == "es" else "English"} as a JSON object.

CV text:
{{text}}
"""
