import pytest
from unittest.mock import patch
from app.services.mlflow_status import check_mlflow_connection
from app.core.config import settings
import requests


@patch("app.services.mlflow_status.settings.MLFLOW_TRACKING_URI", "http://mlflow:5000")
@patch("app.services.mlflow_status.requests.get")
def test_check_mlflow_connection_success(mock_get):
    mock_get.return_value.status_code = 200
    assert check_mlflow_connection() is True
    mock_get.assert_called_once_with("http://mlflow:5000", timeout=1.5)


@patch("app.services.mlflow_status.settings.MLFLOW_TRACKING_URI", "http://mlflow:5000")
@patch("app.services.mlflow_status.requests.get")
def test_check_mlflow_connection_server_error(mock_get):
    mock_get.return_value.status_code = 500
    assert check_mlflow_connection() is False


@patch("app.services.mlflow_status.settings.MLFLOW_TRACKING_URI", "/local/path")
def test_check_mlflow_connection_local_uri():
    assert check_mlflow_connection() is True


@patch("app.services.mlflow_status.settings.MLFLOW_TRACKING_URI", "http://mlflow:5000")
@patch("app.services.mlflow_status.requests.get", side_effect=requests.exceptions.Timeout)
def test_check_mlflow_connection_timeout(mock_get):
    assert check_mlflow_connection() is False


@patch("app.services.mlflow_status.settings.MLFLOW_TRACKING_URI", "http://mlflow:5000")
@patch("app.services.mlflow_status.requests.get", side_effect=Exception("Erro inesperado"))
def test_check_mlflow_connection_unexpected_error(mock_get):
    assert check_mlflow_connection() is False
