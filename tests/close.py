import os
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt
from src import mq
from src import status

import utils


def test_close_process():
    utils.login(status_manager, 'to_ptt_backend', 'to_login_window', 0)
    utils.logout(status_manager, 'to_ptt_backend', 'to_login_window')
    utils.close('to_ptt_backend', 'to_login_window')


def test_login_logout():
    for i in range(3):
        utils.login(status_manager, 'to_ptt_backend', 'to_login_window', 0)
        utils.logout(status_manager, 'to_ptt_backend', 'to_login_window')

        time.sleep(5)


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Test close')

    status.init()
    mq.init()

    status_manager = status.status_manager

    time.sleep(1)

    receiver = threading.Thread(target=mq.receive_message_forever, args=('to_login_window',))
    receiver.start()

    time.sleep(1)

    test_login_logout()

    t = threading.Thread(target=test_close_process, daemon=True)
    t.start()

    receiver.join()
