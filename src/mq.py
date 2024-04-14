import time

import requests

try:
    from . import config
    from . import log
except ImportError:
    import config
    import log


_base_url = f"http://127.0.0.1:{config.config['mq_port']}"

def receive_message():
    logger = log.logger

    while True:
        try:
            response = requests.get(f"{_base_url}/pull/", params={'channel': 'to_backend'})
            message = response.json()
            logger.debug(f"Received message: {message}")
            return message
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            time.sleep(1)


def send_message(message: str):
    logger = log.logger

    if send_socket is None:
        logger.error('MQ is not initialized')
        return

    send_socket.send_string(message)


def init():
    pass
