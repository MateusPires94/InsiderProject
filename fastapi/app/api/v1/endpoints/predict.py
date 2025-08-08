from fastapi import APIRouter, HTTPException
from app.schemas.predict import PredictRequest, PredictResponse
from fastapi import Depends
from app.services.model_service import ModelRegistry, get_model_registry
from app.core.logger import logger

router = APIRouter()

@router.post("/predict",
             summary="Realiza predição com o modelo carregado",
             response_description="Resultado da predição",
             response_model=PredictResponse)
async def predict_route(
    request: PredictRequest,
    model_registry: ModelRegistry = Depends(get_model_registry),
):

    if not model_registry.is_model_loaded():
        logger.warning("Requisição de predição sem modelo carregado.")
        raise HTTPException(status_code=503, detail="Modelo não carregado. Use /load.")

    try:
        inputs = request.dict()["inputs"]
        predictions = await model_registry.predict(inputs)  # Note o await aqui
        logger.info(f"Predição realizada para {len(inputs)} registros.")
        return PredictResponse(predictions=predictions)

    except ValueError as ve:
        logger.warning(f"Erro de validação de dados: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        logger.error(f"Erro interno na predição: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
