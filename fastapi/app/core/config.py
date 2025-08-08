from pydantic import BaseSettings

class Settings(BaseSettings):
    MLFLOW_TRACKING_URI: str
    MLFLOW_MODEL_NAME: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    MONGODB_HISTORY_COLLECTION: str
    MLFLOW_MODEL_ALIAS: str = "champion"


    class Config:
        env_file = ".env"

settings = Settings()