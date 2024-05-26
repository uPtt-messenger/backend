import logging
from typing import Optional

logger = None

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(logging.Formatter(
    fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    datefmt='%m.%d %H:%M:%S'))


def init(log_level: Optional[int] = logging.INFO):
    global logger

    logger = logging.getLogger('main')

    logger.setLevel(log_level)

    if logger.hasHandlers():
        for handler in logger.handlers:
            handler.setFormatter(_console_handler.formatter)
    else:
        logger.addHandler(_console_handler)
