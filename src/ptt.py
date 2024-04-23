import datetime
import threading
import time
import traceback
from typing import Optional

import PyPtt

try:
    from . import log
    from . import status
    from . import mq_message
    from . import message
    from . import mq
    from . import config
except ImportError:
    import log
    import status
    import mq_message
    import message
    import mq
    import config

ptt_api: Optional[PyPtt.Service] = None


def check_new_message():
    logger = log.logger
    status_manager = status.status_manager

    if ptt_api is None:
        logger.error('PTT API not initialized')
        return

    last_mail_date: datetime = None
    start_search_mailbox_index = 1
    first_round = True
    while True:
        time.sleep(config.config['check_ptt_mailbox_interval'])
        if status_manager.status['login'] == status.Status.SUCCESS:
            try:
                current_mail_index = ptt_api.call(
                    'get_newest_index',
                    args={
                        'index_type': PyPtt.NewIndex.MAIL})

                if first_round:
                    first_round = False
                    # find the oldest mail in 14 days using binary search
                    left = 1
                    right = current_mail_index

                    while left <= right:
                        mid = (left + right) // 2

                        mail = None
                        while mail is None:
                            logger.info(f"Get mail: {mid}")
                            mail = ptt_api.call(
                                'get_mail',
                                args={'index': mid})

                            if mail is None:
                                mid -= 1
                                continue

                            if 'date' not in mail or mail['date'] is None:
                                mid -= 1
                                mail = None
                                continue

                        date = datetime.datetime.strptime(mail['date'], '%a %b %d %H:%M:%S %Y')
                        if datetime.datetime.now() - date > datetime.timedelta(
                                days=config.config['search_mailbox_within_days']):
                            left = mid + 1
                            last_mail_date = date
                        else:
                            right = mid - 1

                    start_search_mailbox_index = left - 1

                chat_msg_list = []
                chat_msg_index = []
                mail_date = last_mail_date
                for index in reversed(range(start_search_mailbox_index + 1, current_mail_index + 1)):
                    logger.info(f"Get mail: {index}")
                    mail = ptt_api.call(
                        'get_mail',
                        args={'index': index})

                    if mail is None:
                        continue

                    if 'date' not in mail or mail['date'] is None:
                        continue

                    date = datetime.datetime.strptime(mail['date'], '%a %b %d %H:%M:%S %Y')

                    if date <= last_mail_date:
                        continue

                    if mail_date < date:
                        mail_date = date

                    if 'title' not in mail or mail['title'] is None:
                        continue

                    if not mail['title'].startswith('uPtt chat msg'):
                        continue

                    chat_msg = mq_message.RecvChatMessage(
                        'to_ui',
                        'to_backend',
                        mail['author'],
                        mail['date'],
                        mail['content'])

                    chat_msg_list.append(chat_msg)
                    chat_msg_index.append(index)

                last_mail_date = mail_date
                chat_msg_list = list(reversed(chat_msg_list))

                for chat_msg in chat_msg_list:
                    logger.info(f"Recv chat message: {chat_msg.chat_content}")
                    mq.send_message(chat_msg)

                for index in chat_msg_index:
                    ptt_api.call(
                        'del_mail',
                        args={'index': index})

                start_search_mailbox_index = current_mail_index + 1

            except PyPtt.RequireLogin:
                if status_manager.status['login'] == status.Status.SUCCESS:
                    # if we are logged in, we should reconnect
                    status_manager.status['login'] = status.Status.PENDING
                    login_msg = mq_message.LoginMessage(
                        'to_backend',
                        'to_ui',
                        config.config['ptt_id'],
                        config.config['ptt_pw'])
                    mq.send_message(login_msg)
                continue
            except PyPtt.ConnectionClosed:
                if status_manager.status['login'] == status.Status.SUCCESS:
                    # if we are logged in, we should reconnect
                    status_manager.status['login'] = status.Status.PENDING
                    login_msg = mq_message.LoginMessage(
                        'to_backend',
                        'to_ui',
                        config.config['ptt_id'],
                        config.config['ptt_pw'])
                    mq.send_message(login_msg)
                continue
            except Exception as e:
                traceback.print_exc()
                logger.error(f"ptt module error: {e}")
                continue
        else:
            # reset last mail date
            # it means that we need to check all mails again
            last_mail_date = None
            first_round = True
            start_search_mailbox_index = 1


def init():
    global ptt_api

    ptt_api = PyPtt.Service()

    logger = log.logger

    check_thread = threading.Thread(target=check_new_message, daemon=True)
    check_thread.start()

    logger.info('PTT API initialized')
