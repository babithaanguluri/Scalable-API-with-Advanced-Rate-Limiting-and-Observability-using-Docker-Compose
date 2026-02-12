import pytest
from httpx import AsyncClient
from api.src.main import app

@pytest.mark.asyncio
async def test_api_status():
    """Test the /api/status endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_product_success():
    """Test successful product creation."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "name": "Integration Test Product",
            "description": "Description",
            "price": 99.99
        }
        response = await ac.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Integration Test Product"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_product_validation_error():
    """Test validation error for product creation."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "name": "Invalid Product",
            "description": "Description",
            "price": "not-a-number"
        }
        response = await ac.post("/api/products", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Validation failed for the request body."
    assert any(err["field"] == "body -> price" for err in data["errors"])

@pytest.mark.asyncio
async def test_get_products():
    """Test retrieving products."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_protected_action_success():
    """Test the protected action endpoint."""
    # Note: This might trigger rate limiting if run many times, 
    # but for a fresh test run it should succeed.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"test": "data"}
        response = await ac.post("/api/protected-action", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Action performed successfully"
    assert "X-RateLimit-Limit" in response.headers
