import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "testuser@dopewis.health"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test@12345", "full_name": "Test User"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Test@12345"},
        )
        assert login.status_code == 200
        assert "access_token" in login.json()
