import mlflow
import pandas as pd
from mlflow.pyfunc import PyFuncModel
from mlflow.models import Model
from mlflow.models.signature import ModelSignature
from mlflow.tracking import MlflowClient  # IMPORTAÇÃO ADICIONADA
from app.services.metrics import (
    predictions_total,
    prediction_errors_total,
    model_loads_total,
    model_load_errors_total,
    model_load_duration_seconds,
    inference_duration_seconds,
)
from app.core.logger import logger
from app.core.config import settings
from app.utils import preprocessor, postprocessor

from time import perf_counter
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.history_service import get_history_service

executor = ThreadPoolExecutor()

async def run_predict_sync(model, df_pre):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, model.predict, df_pre)

history_service = get_history_service()

class ModelRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._model = None
            cls._instance._signature = None
            cls._instance._model_uri = None
            cls._instance._input_schema = None
            cls._instance._model_version = None
            cls._instance._model_alias = None
        return cls._instance

    def is_model_loaded(self) -> bool:
        return self._model is not None

    def get_model_uri(self) -> str:
        return self._model_uri

    def get_model_version(self) -> str:
        return self._model_version
    
    def get_model_alias(self) -> str:
        return self._model_alias

    def load_model(self, model_name: str, alias: str = None, version: str = None):
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        client = MlflowClient(tracking_uri=settings.MLFLOW_TRACKING_URI)

        if alias:
            model_uri = f"models:/{model_name}@{alias}"
            version_num = self._get_model_version_from_alias(model_name, alias)
            if not version_num:
                raise RuntimeError(f"Nenhuma versão encontrada para alias/stage '{alias}' no modelo {model_name}")
            version = version_num
        elif version:
            model_uri = f"models:/{model_name}/{version}"
        else:
            raise ValueError("Você deve informar 'alias' ou 'version' para carregar o modelo.")

        logger.info(f"Iniciando carregamento do modelo: {model_uri}")
        start_time = perf_counter()

        try:
            loaded_model = mlflow.pyfunc.load_model(model_uri)
            model_meta = Model.load(model_uri)
            loaded_signature = model_meta.signature
            loaded_input_schema = loaded_signature.inputs if loaded_signature else None

            self._model = loaded_model
            self._signature = loaded_signature
            self._model_uri = model_uri
            self._input_schema = loaded_input_schema
            self._model_version = version
            self._model_alias = alias

            duration = perf_counter() - start_time
            model_loads_total.inc()
            model_load_duration_seconds.observe(duration)

            logger.info(f"Modelo carregado com sucesso em {duration:.2f}s: {model_uri} (versão: {self._model_version})")
            return {"status": "modelo carregado com sucesso", "model_uri": model_uri, "model_version": self._model_version}

        except Exception as e:
            model_load_errors_total.inc()
            logger.error(f"Erro ao carregar o modelo {model_uri}: {str(e)}")
            raise RuntimeError(f"Falha ao carregar modelo {model_uri}: {str(e)}")

    async def predict(self, data: list[dict]):
        if self._model is None:
            logger.error("Tentativa de predição sem modelo carregado.")
            raise RuntimeError("Modelo ainda não foi carregado.")

        start_time = perf_counter()

        try:
            self._validate_input(data)

            df = pd.DataFrame(data)
            logger.info(f"Input de predição recebido com shape {df.shape}")

            df_pre = preprocessor.preprocess(df)

            # Executa a predição síncrona em executor
            preds = await run_predict_sync(self._model, df_pre)

            post_preds = postprocessor.postprocess(preds)

            predictions_total.inc()
            logger.info(f"Predição realizada com sucesso. Total: {len(post_preds)}")

            # Grava histórico no MongoDB (await pois é async)
            await history_service.add(
                input_payload=data,
                output_payload=post_preds,
                model_name=self._model_uri.split("/")[-1].split("@")[0],
                model_version=self._model_version,
                model_alias=self._model_alias
            )

            return post_preds

        except Exception as e:
            prediction_errors_total.inc()
            logger.error(f"Erro durante predição: {str(e)}")
            raise RuntimeError(f"Erro na predição: {str(e)}")

        finally:
            duration = perf_counter() - start_time
            inference_duration_seconds.observe(duration)

    def _validate_input(self, data: list[dict]):
        if self._input_schema is None:
            logger.warning("Input schema não definido, pulando validação.")
            return

        expected_cols = [col.name for col in self._input_schema]

        for i, item in enumerate(data):
            missing_cols = set(expected_cols) - set(item.keys())
            if missing_cols:
                raise ValueError(f"Item {i}: faltando colunas obrigatórias: {missing_cols}")

            for col in self._input_schema:
                col_name = col.name
                expected_type = str(col.type)
                value = item[col_name]

                if expected_type in ("double", "float"):
                    if not isinstance(value, (float, int)):
                        raise ValueError(f"Item {i}: coluna '{col_name}' deve ser float")
                elif expected_type in ("integer", "long"):
                    if not isinstance(value, int):
                        raise ValueError(f"Item {i}: coluna '{col_name}' deve ser int")
                elif expected_type == "string":
                    if not isinstance(value, str):
                        raise ValueError(f"Item {i}: coluna '{col_name}' deve ser string")
                elif expected_type == "boolean":
                    if not isinstance(value, bool):
                        raise ValueError(f"Item {i}: coluna '{col_name}' deve ser booleano")
                else:
                    logger.debug(f"Tipo '{expected_type}' da coluna '{col_name}' não tratado na validação.")

        logger.info("Validação de input concluída com sucesso.")

    def _get_model_version_from_alias(self, model_name: str, alias: str):
        client = MlflowClient()

        versions = client.get_latest_versions(name=model_name, stages=[])

        for v in versions:
            if alias in v.aliases:
                return v.version
        raise ValueError(f"Alias '{alias}' não encontrado para o modelo '{model_name}'")
    
def get_model_registry() -> ModelRegistry:
    return ModelRegistry()

