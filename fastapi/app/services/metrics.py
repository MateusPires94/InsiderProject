from prometheus_client import Counter, Histogram

# Predições
predictions_total = Counter(
    "predictions_total",
    "Total de predições realizadas com sucesso"
)

prediction_errors_total = Counter(
    "prediction_errors_total",
    "Total de falhas durante predição"
)

# Carregamento de modelo
model_loads_total = Counter(
    "model_loads_total",
    "Total de carregamentos de modelo bem-sucedidos"
)

model_load_errors_total = Counter(
    "model_load_errors_total",
    "Total de falhas ao carregar o modelo"
)

model_load_duration_seconds = Histogram(
    "model_load_duration_seconds",
    "Tempo em segundos para carregar o modelo",
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

inference_duration_seconds = Histogram(
    "inference_duration_seconds", 
    "Duração da inferência (s)"
)