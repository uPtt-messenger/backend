import os
import random
import sys
import time

sys.path.append(os.getcwd())

from src import mq_message
from src import mq
from src import status


def login(status_manager: status.StatusManager, id_index: int = None):

    status_manager.status['login'] = status.Status.PENDING
    login_msg = mq_message.LoginMessage(
        'to_backend',
        'to_ui',
        os.environ[f'PTT_ID_{id_index}'],
        os.environ[f'PTT_PW_{id_index}'])

    result = mq.send_message(login_msg)

    while status_manager.status['login'] == status.Status.PENDING and result is not None:
        time.sleep(0.1)


def logout(status_manager: status.StatusManager):
    status_manager.status['logout'] = status.Status.PENDING

    logout_msg = mq_message.LogoutMessage(
        'to_backend',
        'to_ui')

    mq.send_message(logout_msg)
    while status_manager.status['logout'] == status.Status.PENDING:
        time.sleep(0.1)


def close():
    close_msg = mq_message.CloseMessage(
        'to_backend',
        'to_ui')

    mq.send_message(close_msg)
