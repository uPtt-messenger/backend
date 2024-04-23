import os
import sys
import threading
import time

sys.path.append(os.getcwd())

from src import log, ptt, mq_message
from src import mq
from src import status

import utils


def test_process():
    time.sleep(2)

    # login

    status_manager.status['login'] = status.Status.PENDING

    login_msg = mq_message.LoginMessage(
        'to_backend',
        'to_ui',
        os.environ['PTT_ID_0'],
        os.environ['PTT_PW_0'])

    result = mq.send_message(login_msg)

    while status_manager.status['login'] == status.Status.PENDING and result is not None:
        time.sleep(0.1)

    # send chat message
    for i in range(5):
        chat_msg = mq_message.SendChatMessage(
            'to_backend',
            'to_ui',
            os.environ['PTT_ID_1'],
            f'test chat message {i}')

        mq.send_message(chat_msg)

    time.sleep(5)

    status_manager.status['logout'] = status.Status.PENDING
    logout_msg = mq_message.LogoutMessage(
        'to_backend',
        'to_ui')

    result = mq.send_message(logout_msg)
    while status_manager.status['logout'] == status.Status.PENDING and result is not None:
        time.sleep(0.1)

    close_msg = mq_message.SelfCloseMessage(
        'to_backend',
        'to_ui')
    mq.send_message(close_msg)

    logger.info('Test send chat done')


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

    # send chat message
    t = threading.Thread(target=test_process, daemon=True)
    t.start()

    receiver.join()
