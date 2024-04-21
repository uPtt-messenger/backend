import os
import random
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt, message
from src import mq
from src import status


def login():

    # Randomly select a PTT account to login
    id_index = random.randint(0, 1)

    status_manager.status['login'] = status.Status.UNKNOWN
    login_msg = message.LoginMessage(
        'to_backend',
        'to_ui',
        os.environ[f'PTT_ID_{id_index}'],
        os.environ[f'PTT_PW_{id_index}'])

    mq.send_message(login_msg)

    while status_manager.status['login'] == status.Status.UNKNOWN:
        time.sleep(0.1)


def logout():
    status_manager.status['logout'] = status.Status.UNKNOWN

    logout_msg = message.LogoutMessage(
        'to_backend',
        'to_ui')

    mq.send_message(logout_msg)
    while status_manager.status['logout'] == status.Status.UNKNOWN:
        time.sleep(0.1)


def close():
    close_msg = message.CloseMessage(
        'to_backend',
        'to_ui')

    mq.send_message(close_msg)


def test_close_process():

    login()
    logout()
    close()


def test_login_logout():
    for i in range(3):
        login()
        logout()

        time.sleep(5)


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Test close')

    status.init()
    ptt.init()
    mq.init()

    status_manager = status.status_manager

    time.sleep(1)

    receiver = threading.Thread(target=mq.receive_message_forever)
    receiver.start()

    time.sleep(1)

    test_login_logout()

    t = threading.Thread(target=test_close_process, daemon=True)
    t.start()

    receiver.join()