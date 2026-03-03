import logging
import logging.handlers
import os
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)  # ← DEBUG au lieu de INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Terminal → tout voir
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # ← DEBUG au lieu de INFO
    console_handler.setFormatter(formatter)

    # Fichier principal → INFO et plus
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "places_api.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)  # ← fichier garde INFO
    file_handler.setFormatter(formatter)

    # Fichier erreurs → ERROR uniquement
    error_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "errors.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger