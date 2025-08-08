from typing import List, Any, Type, Dict
from pydantic import BaseModel, create_model
from app.services import model_service
from mlflow.types.schema import Schema

class PredictRequest(BaseModel):
    inputs: List[Dict[str, Any]]

class PredictResponse(BaseModel):
    predictions: List[Any]
