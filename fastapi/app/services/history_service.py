import datetime
from typing import List, Tuple
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.logger import logger
from app.db.mongo import history_collection

class HistoryService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def add(self, input_payload, output_payload, model_name, model_version, model_alias=None):
        record = {
            "timestamp": datetime.datetime.utcnow(),
            "input_payload": input_payload,
            "output_payload": output_payload,
            "model_name": model_name,
            "model_version": model_version,
            "model_alias": model_alias
        }
        try:
            await self.collection.insert_one(record)
            logger.info("Histórico de predição salvo com sucesso no MongoDB.")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico no MongoDB: {str(e)}")

    async def list(self, skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
        total = await self.collection.count_documents({})
        cursor = self.collection.find({}).skip(skip).limit(limit).sort("timestamp", -1)
        items = []
        async for doc in cursor:
            doc.pop("_id", None)
            items.append(self._serialize_history_item(doc))
        return items, total

    def _serialize_history_item(self, doc: dict) -> dict:
        return {
            "input_payload": doc.get("input_payload", [{}]),
            "output_payload": doc.get("output_payload", []),
            "model_name": doc.get("model_name", ""),
            "model_alias": doc.get("model_alias", ""),
            "model_version": doc.get("model_version", ""),
            "timestamp": doc["timestamp"].isoformat() if isinstance(doc.get("timestamp"), datetime.datetime) else str(doc.get("timestamp")),
        }
history_service = HistoryService(collection=history_collection)

def get_history_service() -> HistoryService:
    return history_service