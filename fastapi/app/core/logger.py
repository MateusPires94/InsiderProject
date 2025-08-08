from loguru import logger
import os

LOG_FILE = "/var/log/fastapi.log"  

# Remove handler padrão
logger.remove()

# Adiciona novo handler com rotação
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="INFO"
)