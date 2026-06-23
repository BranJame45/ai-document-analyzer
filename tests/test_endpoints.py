import pytest


class TestEndpoints:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_documents_list_unauthorized(self, client):
        response = await client.get("/api/v1/documents")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_templates_unauthorized(self, client):
        response = await client.get("/api/v1/templates")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_templates(self, client, api_key_headers):
        response = await client.get("/api/v1/templates", headers=api_key_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(t["id"] == "cv" for t in data)
        assert any(t["id"] == "invoice" for t in data)
        assert any(t["id"] == "contract" for t in data)

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, client, api_key_headers):
        response = await client.get("/api/v1/documents", headers=api_key_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, client, api_key_headers):
        response = await client.get(
            "/api/v1/documents/00000000-0000-0000-0000-000000000000",
            headers=api_key_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, client, api_key_headers):
        response = await client.delete(
            "/api/v1/documents/00000000-0000-0000-0000-000000000000",
            headers=api_key_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_analyze_no_file(self, client, api_key_headers):
        response = await client.post(
            "/api/v1/analyze",
            headers=api_key_headers,
        )
        assert response.status_code == 422
