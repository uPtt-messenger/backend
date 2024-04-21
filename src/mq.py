import PyPtt
import requests

try:
    from . import config
    from . import log
    from . import ptt
    from . import status
    from . import message
except ImportError:
    import config
    import log
    import ptt
    import status
    import message

_base_url = None

cleared = False


def send_message(msg: message.Message):
    logger = log.logger

    global cleared
    if not cleared:
        logger.info("Clearing messages")
        requests.get(f"{_base_url}/clear/")
        cleared = True

    logger.info(f"Sending message: {msg}")
    response = requests.post(f"{_base_url}/push/", json=msg.to_dict())
    try:
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.info(f"Error: {e}")

    return {}


def receive_message_forever():
    logger = log.logger

    url = f"{_base_url}/pull/"

    params = {
        "channel": 'to_backend'
    }
    status_manager = status.status_manager

    while True:
        try:
            response = requests.get(url, json=params, timeout=config.config['long_polling_timeout'] + 1)
        except requests.exceptions.Timeout:
            logger.info("pull timeout")
            continue
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
        logger.info(f"Pull Message Responses : {response.json()}")

        msg = response.json()
        if 'messages' in msg:
            for msg in msg['messages']:
                logger.info(f"Received message: {msg}")

                reply_channel = msg['reply_channel']

                match msg['category']:
                    case 'close':

                        close_msg = message.CloseMessage(
                            'to_mq_server',
                            'to_backend')

                        send_message(close_msg)

                        logger.info("Received closing command")
                        return
                    case 'login':
                        logger.info("Received login command")

                        if status_manager.status['login'] == status.Status.SUCCESS:
                            logger.info("Already logged in")

                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'already logged in'))
                            continue

                        ptt_id = msg['username']
                        ptt_pw = msg['password']

                        try:
                            ptt.ptt_api.call(
                                'login',
                                {'ptt_id': ptt_id,
                                 'ptt_pw': ptt_pw
                                 })

                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.SUCCESS,
                                    'login success'))

                            status_manager.status['login'] = status.Status.SUCCESS
                        except PyPtt.LoginError:
                            logger.info("Unknown login failed")
                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'unknown login failed'))
                        except PyPtt.WrongIDorPassword:
                            logger.info("Wrong id or password")
                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'wrong id or password'))
                        except PyPtt.OnlySecureConnection:
                            logger.info("Only secure connection")
                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'only secure connection'))
                        except PyPtt.ResetYourContactEmail:
                            logger.info("Reset your contact email")
                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'reset your contact email'))

                    case 'logout':
                        logger.info("Received logout command")

                        ptt.ptt_api.call('logout')

                        status_manager.status['login'] = status.Status.UNKNOWN
                        status_manager.status['logout'] = status.Status.SUCCESS

                    case 'chat':
                        logger.info("Received chat command")

                        if status_manager.status['login'] != status.Status.SUCCESS:
                            logger.info("Not logged in")

                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'not logged in'))
                            continue

                        username = msg['username']
                        chat_message = msg['message']

                        try:
                            ptt.ptt_api.call(
                                'mail',
                                {
                                    'ptt_id': username,
                                    'title': 'uPtt chat message',
                                    'content': chat_message,
                                    'backup': False
                                })

                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.SUCCESS,
                                    'chat success'))
                        except PyPtt.Error as e:
                            logger.info("Send chat failed")
                            send_message(
                                message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    f'Send chat failed: {e}'))
                    case _:
                        logger.info(f"Unknown message: {msg}")

    logger.info("End of receive_message_forever")


def init():
    logger = log.logger
    global _base_url
    _base_url = f"http://127.0.0.1:{config.config['mq_port']}"

    logger.info(f"MQ base url: {_base_url}")
    logger.info("MQ initialized")
