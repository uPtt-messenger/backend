import datetime
import os
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt
from src import mq
from src import status


def test_close_process():
    time.sleep(2)

    status_manager = status.status_manager

    # login

    status_manager.status['login'] = status.Status.UNKNOWN
    mq.send_message('to_backend', {
        'type': 'login',
        'username': os.environ['PTT_ID_0'],
        'password': os.environ['PTT_PW_0'],
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reply_channel': 'to_ui'
    })

    while status_manager.status['login'] == status.Status.UNKNOWN:
        time.sleep(0.1)

    status_manager.status['logout'] = status.Status.UNKNOWN
    mq.send_message('to_backend', {
        'type': 'logout',
        'username': os.environ['PTT_ID_0'],
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })

    while status_manager.status['logout'] == status.Status.UNKNOWN:
        time.sleep(0.1)

    mq.send_message('to_backend', {
        'type': 'close'
    })


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
