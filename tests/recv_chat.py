import os
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt
from src import mq
from src import status
import utils

if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Test chat')

    status.init()
    ptt.init()
    mq.init()

    status_manager = status.status_manager

    receiver = threading.Thread(target=mq.receive_message_forever)
    receiver.start()

    time.sleep(1)

    utils.login(status_manager, 1)

    receiver.join()
