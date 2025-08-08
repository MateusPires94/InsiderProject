import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.services.history_service import HistoryService
from httpx._transports.asgi import ASGITransport


@pytest.fixture
def mock_history_service():
    service = MagicMock(spec=HistoryService)
    service.list = AsyncMock(return_value=([
        {
            "input_payload": [{"x": 1}],
            "output_payload": [0.8],
            "model_name": "modelo",
            "model_version": "1",
            "model_alias": "production",
            "timestamp": "2025-08-06T14:00:00"
        }
    ], 1))
    return service


@pytest.fixture
def override_dependency(mock_history_service):
    from app.services.history_service import get_history_service
    app.dependency_overrides[get_history_service] = lambda: mock_history_service
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.usefixtures("override_dependency")
async def test_get_history_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/history?skip=0&limit=10")

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["total"] == 1
    assert len(json_data["items"]) == 1
    assert json_data["items"][0]["model_name"] == "modelo"


@pytest.mark.asyncio
async def test_get_history_failure(mock_history_service):
    # Override manual aqui porque queremos mudar o comportamento
    from app.services.history_service import get_history_service
    mock_history_service.list.side_effect = Exception("Mongo Error")
    app.dependency_overrides[get_history_service] = lambda: mock_history_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/history?skip=0&limit=10")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Erro interno ao buscar histórico"

    app.dependency_overrides.clear()
