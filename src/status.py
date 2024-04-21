from enum import Enum
from typing import Optional

try:
    from . import log
except ImportError:
    import log


class Status:
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    UNKNOWN = 'UNKNOWN'


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
