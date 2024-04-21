import datetime
import os
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt, message
from src import mq
from src import status


def test_close_process():
    time.sleep(2)

    status_manager = status.status_manager

    # login

    status_manager.status['login'] = status.Status.UNKNOWN

    login_msg = message.LoginMessage(
        'to_backend',
        'to_ui',
        os.environ['PTT_ID_0'],
        os.environ['PTT_PW_0'])

    mq.send_message(login_msg)

    while status_manager.status['login'] == status.Status.UNKNOWN:
        time.sleep(0.1)

    status_manager.status['logout'] = status.Status.UNKNOWN

    logout_msg = message.LogoutMessage(
        'to_backend',
        'to_ui')

    mq.send_message(logout_msg)

    while status_manager.status['logout'] == status.Status.UNKNOWN:
        time.sleep(0.1)

    close_msg = message.CloseMessage(
        'to_backend',
        'to_ui')

    mq.send_message(close_msg)


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Test close')

    status.init()
    ptt.init()
    mq.init()

    t = threading.Thread(target=test_close_process, daemon=True)
    t.start()

    mq.receive_message_forever()
