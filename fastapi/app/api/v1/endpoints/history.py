from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.history_service import HistoryService, get_history_service
from app.schemas.history import HistoryResponse
from app.core.logger import logger

router = APIRouter()

@router.get("/history", response_model=HistoryResponse, summary="Retorna histórico de predições com paginação")
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    history_service: HistoryService = Depends(get_history_service),
):
    try:
        items, total = await history_service.list(skip=skip, limit=limit)
        return HistoryResponse(total=total, skip=skip, limit=limit, items=items)
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar histórico")
