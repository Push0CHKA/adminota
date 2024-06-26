import os
import sys
from enum import Enum

from loguru import logger

from src.core.configuration.settings import get_settings
from src.parser.schemas.vk_api_schemas import VkApiParams

LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | <level>{message}</level>"
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


class ParsLogger:
    def __init__(self, pars_id):
        self.pars_id = pars_id

    def log_msg(self, log: str):
        return f"[Parser №{self.pars_id if self.pars_id  != 0 else VkApiParams.PARSERS_CNT}]: {log}"

    def trace(self, log):
        logger.trace(self.log_msg(log))

    def debug(self, log):
        logger.debug(self.log_msg(log))

    def info(self, log):
        logger.info(self.log_msg(log))

    def warning(self, log):
        logger.warning(self.log_msg(log))

    def success(self, log):
        logger.success(self.log_msg(log))

    def error(self, log):
        logger.error(self.log_msg(log))

    def critical(self, log):
        logger.critical(self.log_msg(log))
