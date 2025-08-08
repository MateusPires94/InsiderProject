from fastapi import APIRouter, HTTPException
from app.services.model_service import ModelRegistry
from app.schemas.load import LoadModelRequest
from app.core.logger import logger

router = APIRouter()

@router.post("/load",
         summary="Carrega um modelo via MLflow",
         response_description="Status do carregamento"
         )
def load(request: LoadModelRequest):
    model_registry = ModelRegistry()
    try:
        request.validate_choice()
        logger.info(f"Requisição para carregar modelo: {request.dict()}")

        result = model_registry.load_model(
            model_name=request.model_name,
            alias=request.alias,
            version=request.version
        )

        return result

    except Exception as e:
        logger.error(f"Erro ao tentar carregar modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
