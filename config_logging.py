# /utils/config_logging.py
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from .app_paths import AppPaths

def setup_logging(file_path: str, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') -> logging.Logger:
    logger_name = Path(file_path).stem + "_logger"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    formatter = logging.Formatter(format)
    log_file = AppPaths.LOG_DIR / f"{logger_name}.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

__all__ = ['setup_logging']
