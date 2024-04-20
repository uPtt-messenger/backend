import json

import PyPtt
import requests

try:
    from . import config
    from . import log
    from . import ptt
    from . import status
except ImportError:
    import config
    import log
    import ptt
    import status

_base_url = None


def send_message(channel: str, message: dict):
    logger = log.logger

    msg = {
        "channel": channel,
        "message": json.dumps(message),
        "reply_channel": "to_backend"
    }

    logger.debug(f"Sending message: {msg}")
    response = requests.post(f"{_base_url}/push/", params=msg)
    logger.debug(f"Sent message: {response.json()}")


def receive_message_forever():
    logger = log.logger

    url = f"{_base_url}/pull/"

    params = {
        "channel": 'to_backend'
    }
    status_manager = status.status_manager

    while True:
        try:
            response = requests.get(url, params=params, timeout=config.config['long_polling_timeout'] + 1)
        except requests.exceptions.Timeout:
            logger.info("Timeout")
            continue
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
        logger.info(f"Pull Message Responses : {response.json()}")

        message = response.json()
        if 'messages' in message:
            for msg in message['messages']:
                logger.info(f"Received message: {msg}")

                match msg['type']:
                    case 'close':
                        logger.info("Received closing command")
                        return
                    case 'login':
                        logger.info("Received login command")

                        reply_channel = msg['reply_channel']

                        if status_manager.status['login'] == status.Status.SUCCESS:
                            logger.info("Already logged in")
                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'failed',
                                'message': 'already logged in'
                            })
                            continue

                        ptt_id = msg['username']
                        ptt_pw = msg['password']

                        try:
                            ptt.ptt_api.call(
                                'login',
                                {'ptt_id': ptt_id,
                                 'ptt_pw': ptt_pw
                                 })

                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'success',
                                'id': ptt_id
                            })
                            status_manager.status['login'] = status.Status.SUCCESS
                        except PyPtt.LoginError:
                            logger.info("Unknown login failed")
                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'failed',
                                'message': 'unknown login error'
                            })
                        except PyPtt.WrongIDorPassword:
                            logger.info("Wrong id or password")
                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'failed',
                                'message': 'wrong id or password'
                            })
                        except PyPtt.OnlySecureConnection:
                            logger.info("Only secure connection")
                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'failed',
                                'message': 'only secure connection'
                            })
                        except PyPtt.ResetYourContactEmail:
                            logger.info("Reset your contact email")
                            send_message(reply_channel, {
                                'type': 'login_status',
                                'status': 'failed',
                                'message': 'set contact email first'
                            })

                    case 'logout':
                        logger.info("Received logout command")

                        ptt.ptt_api.call('logout')

                        status_manager.status['login'] = status.Status.UNKNOWN
                        status_manager.status['logout'] = status.Status.SUCCESS

                    case _:
                        logger.info(f"Unknown message: {msg}")

        logger.info("No more messages")

    logger.info("End of receive_message_forever")


def init():
    logger = log.logger
    global _base_url
    _base_url = f"http://127.0.0.1:{config.config['mq_port']}"

    logger.info(f"MQ base url: {_base_url}")
    logger.info("MQ initialized")
