import time
from typing import Optional

import PyPtt

try:
    from . import log
    from . import status
except ImportError:
    import log
    import status

ptt_api: Optional[PyPtt.Service] = None


def check_new_message():
    logger = log.logger
    status_manager = status.status_manager

    if ptt_api is None:
        logger.error('PTT API not initialized')
        return

    how_many_messages = 0
    total_messages = 0
    while True:
        if status_manager.status['login'] == status.Status.SUCCESS:
            try:
                how_many_messages = ptt_api.call(
                    'get_newest_index',
                    args={
                        'index_type': PyPtt.NewIndex.MAIL,
                        'search_list': [(PyPtt.SearchType.KEYWORD, 'uPtt chat message')]})

                if how_many_messages > 0:

                    logger.info(f'New messages: {how_many_messages}')

                    current_total_messages = ptt_api.call(
                        'get_newest_index',
                        args={
                            'index_type': PyPtt.NewIndex.MAIL})

                    logger.info(f'Current total messages: {current_total_messages}')

                    for i in reversed(range(total_messages + 1, current_total_messages + 1)):
                        logger.info(f'Checking mail: {i}')
                        mail = ptt_api.call('get_mail', args={
                            'index': i
                        })
                        logger.info(f'New mail: {mail}')

                    total_messages = current_total_messages
            except Exception as e:
                logger.error(f'Error: {e}')
                continue

        time.sleep(3)


def init():
    global ptt_api

    ptt_api = PyPtt.Service()

    logger = log.logger

    logger.info('PTT API initialized')
