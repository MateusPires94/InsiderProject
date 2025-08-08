from pydantic import BaseModel
from typing import List, Dict, Any

class HistoryItem(BaseModel):
    input_payload: List[Dict[str, Any]]
    output_payload: List
    model_name: str
    model_alias: str
    model_version: str
    timestamp: str

class HistoryResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[HistoryItem]