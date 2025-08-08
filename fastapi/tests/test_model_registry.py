import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.model_service import ModelRegistry
from mlflow.exceptions import MlflowException
from types import SimpleNamespace


@pytest.fixture
def model_registry():
    # Limpa o singleton antes de cada teste
    ModelRegistry._instance = None
    return ModelRegistry()


@patch("app.services.model_service.mlflow.pyfunc.load_model")
@patch("app.services.model_service.Model.load")
@patch("app.services.model_service.MlflowClient")
def test_load_model_success(mock_client_class, mock_model_load, mock_pyfunc_load, model_registry):
    mock_model = MagicMock()
    mock_signature = MagicMock()
    mock_signature.inputs = [MagicMock(name="col1", type="string")]
    mock_model_load.return_value.signature = mock_signature
    mock_pyfunc_load.return_value = "modelo carregado"

    mock_client = MagicMock()
    mock_client.get_latest_versions.return_value = [
        MagicMock(aliases=["production"], version="5")
    ]
    mock_client_class.return_value = mock_client

    result = model_registry.load_model(model_name="titanic_model", alias="production")
    
    assert model_registry.is_model_loaded()
    assert result["status"] == "modelo carregado com sucesso"
    assert result["model_version"] == "5"
    assert "model_uri" in result


@patch("app.services.model_service.mlflow.pyfunc.load_model", side_effect=MlflowException("erro"))
@patch("app.services.model_service.Model.load")
@patch("app.services.model_service.MlflowClient")
def test_load_model_failure(mock_client_class, mock_model_load, mock_pyfunc_load, model_registry):
    mock_client = MagicMock()
    mock_client.get_latest_versions.return_value = [
        MagicMock(aliases=["production"], version="1")
    ]
    mock_client_class.return_value = mock_client

    with pytest.raises(RuntimeError, match="Falha ao carregar modelo"):
        model_registry.load_model("titanic_model", alias="production")



def test_validate_input_success(model_registry):
    mock_schema = [SimpleNamespace(name="col1", type="string")]
    model_registry._input_schema = mock_schema
    data = [{"col1": "abc"}]

    model_registry._validate_input(data)


def test_validate_input_missing_field(model_registry):
    model_registry._input_schema = [MagicMock(name="col1", type="string")]
    data = [{}]

    with pytest.raises(ValueError, match="faltando colunas obrigatórias"):
        model_registry._validate_input(data)


@pytest.mark.asyncio
@patch("app.services.model_service.run_predict_sync", return_value=[1])
@patch("app.services.model_service.preprocessor.preprocess", return_value="df_pre")
@patch("app.services.model_service.postprocessor.postprocess", return_value=[1])
@patch("app.services.model_service.history_service.add", new_callable=AsyncMock)
async def test_predict_success(mock_add, mock_post, mock_pre, mock_run, model_registry):
    model_registry._model = MagicMock()
    model_registry._input_schema = None  # pula validação
    model_registry._model_uri = "models:/titanic_model@production"
    model_registry._model_version = "2"
    model_registry._model_alias = "production"

    data = [{"feature1": 1}]
    result = await model_registry.predict(data)

    assert result == [1]
    mock_add.assert_awaited_once()
    mock_pre.assert_called_once()
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_predict_without_model(model_registry):
    with pytest.raises(RuntimeError, match="Modelo ainda não foi carregado"):
        await model_registry.predict([{"feature1": 1}])


@pytest.mark.asyncio
@patch("app.services.model_service.run_predict_sync", return_value=[1])
@patch("app.services.model_service.preprocessor.preprocess", return_value="df_pre")
@patch("app.services.model_service.postprocessor.postprocess", return_value=[1])
@patch("app.services.model_service.history_service.add", new_callable=AsyncMock)
async def test_predict_validation_error(mock_add, mock_post, mock_pre, mock_run, model_registry):
    model_registry._model = MagicMock()
    model_registry._input_schema = [MagicMock(name="col1", type="string")]
    model_registry._model_uri = "models:/titanic_model@production"
    model_registry._model_version = "2"
    model_registry._model_alias = "production"

    data = [{"wrong_col": "abc"}]

    with pytest.raises(RuntimeError, match="Erro na predição"):
        await model_registry.predict(data)


def test_get_model_uri_version_alias(model_registry):
    model_registry._model_uri = "models:/titanic_model@production"
    model_registry._model_version = "3"
    model_registry._model_alias = "production"

    assert model_registry.get_model_uri() == "models:/titanic_model@production"
    assert model_registry.get_model_version() == "3"
    assert model_registry.get_model_alias() == "production"
