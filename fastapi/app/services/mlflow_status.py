
from app.core.config import settings
from app.core.logger import logger
import requests
from app.core.config import settings

def check_mlflow_connection(timeout=1.5):
    try:
        tracking_uri = settings.MLFLOW_TRACKING_URI

        if tracking_uri.startswith("http"):
            response = requests.get(tracking_uri, timeout=timeout)
            return response.status_code < 500
        else:
            return True  # se for local
    except requests.exceptions.Timeout:
        logger.error("Timeout ao tentar conectar com o MLflow.")
        return False
    except Exception as e:
        logger.error(f"Erro ao checar o MLflow: {str(e)}")
        return False
    
def get_mlflow_status():
    return check_mlflow_connection()