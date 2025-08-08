from fastapi import FastAPI
from app.api.v1.endpoints import predict, load, health, history
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="FastAPI + MLflow Model API",
    version="1.0.0"
)

# Middleware Prometheus
Instrumentator().instrument(app).expose(
    app, 
    include_in_schema=False,
    endpoint="/metrics",
    tags=["Metrics"]
)

# Rotas principais
app.include_router(health.router, prefix="/v1")
app.include_router(load.router, prefix="/v1", tags=["Model Loader"])
app.include_router(predict.router, prefix="/v1", tags=["Predict"])
app.include_router(history.router, prefix="", tags=["history"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)