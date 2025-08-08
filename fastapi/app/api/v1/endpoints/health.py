from fastapi import APIRouter, Request, Depends
from app.services.model_service import ModelRegistry, get_model_registry
from app.services.mlflow_status import get_mlflow_status
from app.services.mongo_status import get_mongo_status
from app.core.config import settings

router = APIRouter()

@router.get("/health", tags=["Health Check"])
async def health_check(
    request: Request,
    model_registry: ModelRegistry = Depends(get_model_registry),
    mlflow_ok: bool = Depends(get_mlflow_status),
    mongo_ok: bool = Depends(get_mongo_status),
):
    prometheus_ok = any(route.path == "/metrics" for route in request.app.routes)

    return {
        "status": "ok",
        "model_loaded": model_registry.is_model_loaded(),
        "mlflow_tracking_uri": settings.MLFLOW_TRACKING_URI,
        "mlflow_reachable": mlflow_ok,
        "mongodb_reachable": mongo_ok,
        "prometheus_metrics_available": prometheus_ok
    }
