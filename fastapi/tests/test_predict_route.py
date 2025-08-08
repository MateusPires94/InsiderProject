import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.services.model_service import get_model_registry


@pytest.fixture
def mock_model_registry():
    mock = MagicMock()
    mock.is_model_loaded.return_value = True
    mock.predict = AsyncMock(return_value=["aprovado", "reprovado"])
    return mock


@pytest.fixture(autouse=True)
def override_model_registry(mock_model_registry):
    app.dependency_overrides[get_model_registry] = lambda: mock_model_registry
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_predict_success(mock_model_registry):
    mock_model_registry.is_model_loaded.return_value = True
    mock_model_registry.predict.return_value = ["aprovado", "reprovado"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/predict", json={"inputs": [{"age": 30}, {"age": 18}]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"predictions": ["aprovado", "reprovado"]}
    mock_model_registry.predict.assert_awaited_once_with([{"age": 30}, {"age": 18}])


@pytest.mark.asyncio
async def test_predict_model_not_loaded(mock_model_registry):
    mock_model_registry.is_model_loaded.return_value = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/predict", json={"inputs": [{"age": 30}]})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Modelo não carregado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_predict_validation_error(mock_model_registry):
    mock_model_registry.predict.side_effect = ValueError("entrada inválida")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/predict", json={"inputs": [{"age": -1}]})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "entrada inválida" in response.json()["detail"]


@pytest.mark.asyncio
async def test_predict_internal_error(mock_model_registry):
    mock_model_registry.predict.side_effect = Exception("erro inesperado")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/predict", json={"inputs": [{"age": 99}]})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "erro inesperado" in response.json()["detail"]
