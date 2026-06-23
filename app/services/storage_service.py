from app.config import settings


async def upload_file(file_bytes: bytes, filename: str) -> str | None:
    try:
        from supabase import create_client

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        bucket = settings.SUPABASE_BUCKET

        response = supabase.storage.from_(bucket).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": "application/octet-stream"},
        )

        public_url = supabase.storage.from_(bucket).get_public_url(filename)
        return public_url

    except Exception as e:
        print(f"Storage upload failed: {e}")
        return None
