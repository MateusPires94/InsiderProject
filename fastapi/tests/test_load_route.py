from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_load_success():
    with patch("app.api.v1.endpoints.load.ModelRegistry.load_model") as mock_load_model:
        mock_load_model.return_value = {
            "status": "modelo carregado com sucesso",
            "model_uri": "models:/modelo_teste@production"
        }
        response = client.post("/v1/load", json={"model_name": "modelo_teste", "alias": "production"})
        assert response.status_code == 200
        assert "model_uri" in response.json()

def test_load_failure():
    with patch("app.api.v1.endpoints.load.ModelRegistry.load_model", side_effect=Exception("Erro")):
        response = client.post("/v1/load", json={"model_name": "modelo_teste", "alias": "production"})
        assert response.status_code == 500
