import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers.
    File handler captures DEBUG+, console handler captures INFO+.
    """
    os.makedirs("logs", exist_ok=True)

    log_filename = f"logs/trading_bot_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger