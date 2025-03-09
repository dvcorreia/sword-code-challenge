from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from logging import getLevelNamesMapping
from typing import Iterable

import structlog
from structlog.typing import Processor


class LogFormat(StrEnum):
    TEXT = "text"
    JSON = "json"


@dataclass
class Config:
    level: str = "INFO"
    format: LogFormat = LogFormat.TEXT


_shared_text_processors: Iterable[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.TimeStamper(),
    structlog.dev.ConsoleRenderer(),
]

_shared_json_processors: Iterable[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.TimeStamper(),
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    structlog.processors.JSONRenderer(),
]


def setup_logging(config: Config):
    level = getLevelNamesMapping()[config.level]
    processors = (
        _shared_text_processors
        if config.format is LogFormat.TEXT
        else _shared_json_processors
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
    )
