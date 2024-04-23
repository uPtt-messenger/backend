import traceback

import PyPtt
import requests

try:
    from . import config
    from . import log
    from . import ptt
    from . import status
    from . import mq_message
except ImportError:
    import config
    import log
    import ptt
    import status
    import mq_message

_base_url = None


def send_message(msg: mq_message.Message):
    logger = log.logger

    logger.info(f"Sending message: {msg}")
    try:
        response = requests.post(f"{_base_url}/push/", json=msg.to_dict())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.info("Push msg to mq server connection error")
    except Exception as e:
        logger.info(f"MQ push error: {e}")

    return None


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
        except requests.exceptions.ConnectionError:
            logger.info("MQ server connection error")
            break
        except Exception as e:
            traceback.print_exc()
            logger.error(f"MQ pull error: {e}")
            continue

        msg = response.json()

        if 'messages' in msg:
            if msg['messages']:
                logger.info(f"Pull Message Responses: {msg}")

            for msg in msg['messages']:
                logger.info(f"Received message: {msg}")

                reply_channel = msg['reply_channel']

                match msg['category']:
                    case 'close':

                        close_msg = mq_message.CloseMessage(
                            'to_mq_server',
                            'to_backend')

                        send_message(close_msg)

                        logger.info("Received close command")
                        return

                    case 'self_close':
                        logger.info("Received self_close command")
                        return
                    case 'login':
                        logger.info("Received login command")

                        if status_manager.status['login'] == status.Status.SUCCESS:
                            logger.info("Already logged in")

                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'already logged in'))
                            continue

                        ptt_id = msg['username']
                        ptt_pw = msg['password']

                        # save ptt_id and ptt_pw for re-login automatically
                        config.config['ptt_id'] = ptt_id
                        config.config['ptt_pw'] = ptt_pw

                        try:
                            ptt.ptt_api.call(
                                'login',
                                {'ptt_id': ptt_id,
                                 'ptt_pw': ptt_pw
                                 })

                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.SUCCESS,
                                    'login success'))

                            status_manager.status['login'] = status.Status.SUCCESS
                        except PyPtt.LoginError:
                            logger.info("Unknown login failed")
                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'unknown login failed'))
                        except PyPtt.WrongIDorPassword:
                            logger.info("Wrong id or password")
                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'wrong id or password'))
                        except PyPtt.OnlySecureConnection:
                            logger.info("Only secure connection")
                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'only secure connection'))
                        except PyPtt.ResetYourContactEmail:
                            logger.info("Reset your contact email")
                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.FAILURE,
                                    'reset your contact email'))

                    case 'logout':
                        logger.info("Received logout command")

                        ptt.ptt_api.call('logout')

                        status_manager.status['login'] = status.Status.UNKNOWN
                        status_manager.status['logout'] = status.Status.SUCCESS

                    case 'send_chat':
                        logger.info("Received send_chat command")

                        if status_manager.status['login'] != status.Status.SUCCESS:
                            logger.info("Not logged in")

                            send_message(
                                mq_message.StatusMessage(
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
                                    'title': f'uPtt chat msg',
                                    'content': chat_message,
                                    'backup': False
                                })

                            send_message(
                                mq_message.StatusMessage(
                                    reply_channel,
                                    'to_backend',
                                    status.Status.SUCCESS,
                                    'chat success'))
                        except PyPtt.Error as e:
                            logger.info("Send chat failed")
                            send_message(
                                mq_message.StatusMessage(
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
