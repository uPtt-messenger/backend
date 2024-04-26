import argparse
import logging

import log
import mq
import ptt
import status
import version


def init():
    parser = argparse.ArgumentParser()

    parser.add_argument('--test', action='store_true', help='Run test mode')
    args = parser.parse_args()

    log.init(logging.DEBUG if args.test else logging.INFO)
    logger = log.logger

    logger.info(f'Welcome to uPtt backend v {version.__version__}!')
    logger.debug('======== DEBUG MODE ========')

    status.init()
    ptt.init()
    mq.init()

    mq.receive_message_forever()


if __name__ == '__main__':
    init()
