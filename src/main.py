import argparse
import logging

import __init__
import log
import mq
import ptt


def init():
    parser = argparse.ArgumentParser()

    parser.add_argument('--test', action='store_true', help='Run test mode')
    args = parser.parse_args()

    log.init(logging.DEBUG if args.test else logging.INFO)
    logger = log.logger

    logger.info(f'Welcome to uPtt backend v {__init__.__version__}!')
    logger.debug('======== DEBUG MODE ========')

    ptt.init()
    mq.init()


if __name__ == '__main__':
    init()
