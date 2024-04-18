import json
import os
import sys
import threading
import time

import requests

sys.path.append(os.getcwd())

from src import log
from src import config

base_url = f"http://127.0.0.1:{config.config['mq_port']}"


def test_push_message(channel, count):
    url = f"{base_url}/push/"

    for i in range(count):
        test_msg = {
            "name": "test",
            "value": i
        }

        params = {
            "channel": channel,
            "message": json.dumps(test_msg)
        }

        logger.info(f"Pushing message to {channel}: {test_msg}")
        response = requests.post(url, params=params)
        logger.info(f"Push Message Response: {response.json()}")

        time.sleep(0.5)


def test_pull_message(channel):
    url = f"{base_url}/pull/"

    params = {
        "channel": channel
    }

    start_time = time.time()

    while time.time() - start_time < 30:
        try:
            response = requests.get(url, params=params, timeout=config.config['long_polling_timeout'] + 1)
        except requests.exceptions.Timeout:
            logger.info("Timeout")
            continue
        logger.info(f"Pull Message Response from {channel}: {response.json()}")


def test_invalid_channel():
    url = f"{base_url}/push/"

    test_msg = {
        "name": "test",
        "value": 0
    }

    params = {
        "channel": "invalid_channel",
        "message": json.dumps(test_msg)
    }

    logger.info(f"Pushing message to invalid channel: {test_msg}")
    response = requests.post(url, params=params)
    logger.info(f"Push Message Response: {response.json()}")


def test_invalid_message():
    url = f"{base_url}/push/"

    test_msg = "invalid message"

    params = {
        "channel": "to_backend",
        "message": test_msg
    }

    logger.info(f"Pushing invalid message: {test_msg}")
    response = requests.post(url, params=params)
    logger.info(f"Push Message Response: {response.json()}")


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Starting tests')

    # Test pushing and pulling messages from different channels
    channels = ['to_backend', 'to_ui', 'to_system_tray', 'to_notification']
    for channel in channels:
        t = threading.Thread(target=test_push_message, args=(channel, 10))
        t.start()
        test_pull_message(channel)
        t.join()

    # Test pushing and pulling large number of messages
    t = threading.Thread(target=test_push_message, args=('to_backend', 100))
    t.start()
    test_pull_message('to_backend')
    t.join()

    # Test invalid channel and message format
    test_invalid_channel()
    test_invalid_message()