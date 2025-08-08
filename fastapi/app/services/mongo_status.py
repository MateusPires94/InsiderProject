# app/services/mongo_status.py
from app.db.mongo import history_collection

async def check_mongo_connection() -> bool:
    try:
        await history_collection.database.command("ping")
        return True
    except Exception:
        return False

async def get_mongo_status():
    return await check_mongo_connection()
