def get_prompt(lang: str) -> str:
    return f"""
You are a contract analysis assistant. Extract the following information from the contract text:

- Parties involved
- Contract object / purpose
- Start date
- End date
- Amounts / financial terms
- Main clauses (list)
- Signatures (if present)

Respond in {"Spanish" if lang == "es" else "English"} as a JSON object.

Contract text:
{{text}}
"""
