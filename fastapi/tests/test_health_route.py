import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from unittest.mock import MagicMock
from fastapi import status

from app.main import app
from app.services.model_service import get_model_registry
from app.services.mlflow_status import get_mlflow_status
from app.services.mongo_status import get_mongo_status


@pytest.fixture
def mock_model_registry():
    mock = MagicMock()
    mock.is_model_loaded.return_value = True
    return mock


@pytest.fixture
def override_dependencies(mock_model_registry):
    app.dependency_overrides[get_model_registry] = lambda: mock_model_registry
    app.dependency_overrides[get_mlflow_status] = lambda: True
    app.dependency_overrides[get_mongo_status] = lambda: True
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.usefixtures("override_dependencies")
async def test_health_check_success():
    # Garante que a rota /metrics existe na aplicação (usado para Prometheus)
    app.router.routes.append(
        type("MockRoute", (), {"path": "/metrics"})()
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["mlflow_reachable"] is True
    assert data["mongodb_reachable"] is True
    assert data["prometheus_metrics_available"] is True


@pytest.mark.asyncio
async def test_health_check_with_dependencies_down():
    # Mocks alternativos para dependências com falha
    app.dependency_overrides[get_model_registry] = lambda: MagicMock(is_model_loaded=lambda: False)
    app.dependency_overrides[get_mlflow_status] = lambda: False
    app.dependency_overrides[get_mongo_status] = lambda: False

    # Remove a rota /metrics se ela existir (simulando ausência do Prometheus)
    app.router.routes = [r for r in app.router.routes if r.path != "/metrics"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["model_loaded"] is False
    assert data["mlflow_reachable"] is False
    assert data["mongodb_reachable"] is False
    assert data["prometheus_metrics_available"] is False

    app.dependency_overrides.clear()
