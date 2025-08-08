import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.history_service import HistoryService
import datetime

@pytest.mark.asyncio
async def test_add_history():
    mock_collection = AsyncMock()
    history_service = HistoryService(collection=mock_collection)

    await history_service.add(
        input_payload={"x": 1},
        output_payload=[0.9],
        model_name="modelo",
        model_version="1",
        model_alias="prod"
    )

    mock_collection.insert_one.assert_awaited_once()
    args, _ = mock_collection.insert_one.await_args
    inserted_doc = args[0]
    assert inserted_doc["input_payload"] == {"x": 1}
    assert inserted_doc["output_payload"] == [0.9]
    assert inserted_doc["model_name"] == "modelo"
    assert inserted_doc["model_version"] == "1"
    assert inserted_doc["model_alias"] == "prod"
    assert "timestamp" in inserted_doc

@pytest.mark.asyncio
async def test_list_history():
    # Documento simulado no Mongo
    doc = {
        "_id": "123",
        "input_payload": {"x": 1},
        "output_payload": [0.9],
        "model_name": "modelo",
        "model_version": "1",
        "model_alias": "prod",
        "timestamp": datetime.datetime(2025, 8, 6, 14, 0, 0)
    }

    # Mock do cursor
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = mock_cursor

    # Corrige __aiter__ para ser uma função que retorna um async generator
    async def async_generator():
        yield doc

    mock_cursor.__aiter__ = lambda self=mock_cursor: async_generator()

    # Mock da collection
    mock_collection = MagicMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)
    mock_collection.count_documents = AsyncMock(return_value=5)

    # Instancia o serviço
    history_service = HistoryService(collection=mock_collection)

    # Chama o método a ser testado
    items, total = await history_service.list(skip=0, limit=10)

    # Asserts
    assert total == 5
    assert len(items) == 1
    item = items[0]
    assert item["model_name"] == "modelo"
    assert item["input_payload"] == {"x": 1}
    assert item["output_payload"] == [0.9]
    assert item["model_version"] == "1"
    assert item["model_alias"] == "prod"
    assert item["timestamp"] == "2025-08-06T14:00:00"
