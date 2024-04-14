import json
import os
import sys

import requests

sys.path.append(os.getcwd())

from src import log
from src import config

base_url = f"http://127.0.0.1:{config.config['mq_port']}"


def test_push_message():
    url = f"{base_url}/push/"

    test_msg = {
        "name": "test",
        "age": 20
    }

    params = {
        "channel": "to_backend",
        "message": json.dumps(test_msg)
    }

    response = requests.post(url, params=params)
    logger.info(f"Push Message Response: {response.json()}")


def test_pull_message():
    url = f"{base_url}/pull/"

    params = {
        "channel": 'to_backend'
    }

    response = requests.get(url, params=params)
    logger.info(f"Pull Message Response: {response.json()}")


if __name__ == '__main__':
    log.init()

    logger = log.logger

    logger.info('Starting tests')
    test_push_message()
    test_pull_message()
