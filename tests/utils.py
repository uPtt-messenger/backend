import os
import random
import sys
import time

sys.path.append(os.getcwd())

from src import message
from src import mq
from src import status


def login(status_manager: status.StatusManager):
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


def logout(status_manager: status.StatusManager):
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
