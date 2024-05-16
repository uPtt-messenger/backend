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
    try:
        time.sleep(2)

        # login
        utils.login(status_manager, 'to_ptt_backend', 'to_login_window', 0)

        # send chat message
        for i in range(5):
            chat_msg = mq_message.SendChatMessage(
                'to_ptt_backend',
                'to_login_window',
                os.environ['PTT_ID_1'],
                f'test chat message {i}')

            mq.send_message(chat_msg)

        logger.info('Test send chat done')
    finally:
        utils.logout(status_manager, 'to_ptt_backend', 'to_login_window')
        utils.self_close('to_login_window', 'to_ptt_backend')


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Test chat')

    status.init()
    mq.init()

    status_manager = status.status_manager

    receiver = threading.Thread(target=mq.receive_message_forever, args=('to_login_window',))
    receiver.start()

    time.sleep(1)

    # send chat message
    t = threading.Thread(target=test_process, daemon=True)
    t.start()

    receiver.join()
