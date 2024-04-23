import os
import sys
import time

sys.path.append(os.getcwd())

from src import mq_message
from src import mq
from src import status


def login(status_manager: status.StatusManager, channel: str, reply_channel: str, id_index: int = None):
    status_manager.status['login'] = status.Status.PENDING
    login_msg = mq_message.LoginMessage(
        channel,
        reply_channel,
        os.environ[f'PTT_ID_{id_index}'],
        os.environ[f'PTT_PW_{id_index}'])

    result = mq.send_message(login_msg)

    while status_manager.status['login'] == status.Status.PENDING and result is not None:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break


def logout(status_manager: status.StatusManager, channel: str, reply_channel: str):
    status_manager.status['logout'] = status.Status.PENDING

    logout_msg = mq_message.LogoutMessage(
        channel,
        reply_channel)

    mq.send_message(logout_msg)
    while status_manager.status['logout'] == status.Status.PENDING:
        time.sleep(0.1)


def close(channel: str, reply_channel: str):
    close_msg = mq_message.CloseMessage(
        channel,
        reply_channel)

    mq.send_message(close_msg)


def self_close(channel: str, reply_channel: str):
    close_msg = mq_message.SelfCloseMessage(
        channel,
        reply_channel)

    mq.send_message(close_msg)
