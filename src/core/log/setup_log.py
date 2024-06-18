import os
import sys
from enum import Enum

from loguru import logger

from src.core.configuration.settings import get_settings

LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


class LogLevel(Enum):
    trace = "TRACE"
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    success = "SUCCESS"
    error = "ERROR"
    critical = "CRITICAL"

    @classmethod
    def list(cls):
        return list(map(lambda e: e.value, cls))


def reinit_logger(log_level: str, log_path: str | None):
    log_level = (
        LogLevel.info.value
        if log_level not in LogLevel.list()
        else get_settings().log.level
    )
    logger.remove()
    logger.add(sys.stderr, format=LOGGER_FORMAT, level=log_level)
    if log_path:
        os.makedirs(os.path.abspath(log_path), exist_ok=True)
        logger.log(log_level, f"log dir: {os.path.abspath(log_path)}")
        logger.add(
            log_path + "/",
            format=LOGGER_FORMAT,
            level=log_level,
            rotation="1 week",
        )
    logger.log(log_level, "logger re-inited")
