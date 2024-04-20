from logging import Logger
from typing import Optional

import PyPtt

try:
    from . import log
except ImportError:
    import log

ptt_api = None
logger: Optional[Logger] = None


def init():
    global ptt_api
    global logger

    ptt_api = PyPtt.Service()

    logger = log.logger

    logger.info('PTT API initialized')
