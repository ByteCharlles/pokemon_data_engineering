import sys
from loguru import logger

# Remove handler padrão do loguru
logger.remove()

# Handler para output no terminal (stderr) com formatação customizada
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Handler para armazenamento em arquivo rotativo
logger.add("logs/app.log", rotation="500 MB", level="INFO")

__all__ = ["logger"]