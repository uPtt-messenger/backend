from enum import Enum
from typing import Optional

try:
    from . import log
except ImportError:
    import log


class Status(Enum):
    SUCCESS = 0
    FAILURE = 1
    UNKNOWN = 2


class StatusManager:
    """
    管理狀態相關資料的類別。
    """

    def __init__(self):
        self.status = {}


status_manager: Optional[StatusManager] = None


def init():
    logger = log.logger

    global status_manager
    status_manager = StatusManager()

    logger.info('StatusManager initialized')
