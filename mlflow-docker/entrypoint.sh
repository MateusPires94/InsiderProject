#!/bin/bash

# Criar o bucket no MinIO (se não existir)
python create_bucket.py

# Rodar o mlflow server
mlflow server \
    --backend-store-uri $MLFLOW_BACKEND_STORE_URI \
    --default-artifact-root $MLFLOW_DEFAULT_ARTIFACT_ROOT \
    --host 0.0.0.0