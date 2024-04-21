import json
import os
import sys
import threading
import time

import requests

sys.path.append(os.getcwd())

from src import message
from src import log
from src import config

base_url = f"http://127.0.0.1:{config.config['mq_port']}"


def test_push_message(channel, count, interval=0):
    url = f"{base_url}/push/"

    for i in range(count):
        test_msg = message.Message(channel, channel, {
            'name': 'test',
            'value': i
        })

        logger.info(f"Pushing message to {channel}: {test_msg}")
        response = requests.post(url, json=test_msg.to_dict())
        logger.info(f"Push Message Response: {response.json()}")

        time.sleep(interval)


def test_pull_message(channel):
    url = f"{base_url}/pull/"

    params = {
        "channel": channel
    }

    start_time = time.time()

    while time.time() - start_time < 30:
        try:
            response = requests.get(url, json=params, timeout=config.config['long_polling_timeout'] + 1)
        except requests.exceptions.Timeout:
            logger.info("pull timeout")
            break
        logger.info(f"Pull Message Response from {channel}: {response.json()}")

        if 'messages' in response.json():
            if len(response.json()['messages']) == 0:
                break


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
    response = requests.post(url, json=params)
    logger.info(f"Push Message Response: {response.json()}")


def test_invalid_message():
    url = f"{base_url}/push/"

    test_msg = "invalid message"

    params = {
        "channel": "to_backend",
        "message": test_msg
    }

    logger.info(f"Pushing invalid message: {test_msg}")
    response = requests.post(url, json=params)
    logger.info(f"Push Message Response: {response.json()}")


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Starting tests')

    test_push_message('to_backend', 5)
    test_pull_message('to_backend')

    test_invalid_channel()
    test_invalid_message()

    t0 = threading.Thread(target=test_push_message, args=('to_backend', 10, 1), daemon=True)
    t0.start()

    t1 = threading.Thread(target=test_pull_message, args=('to_backend',), daemon=True)
    t1.start()

    t0.join()
    t1.join()


