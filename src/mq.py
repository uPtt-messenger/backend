try:
    from . import config
    from . import log
except ImportError:
    import config
    import log


def receive_message():
    logger = log.logger

    if recv_socket is None:
        logger.error('MQ is not initialized')
        return

    while True:
        message = recv_socket.recv_string()
        logger.info(f"Received message: {message}")


def send_message(message: str):
    logger = log.logger

    if send_socket is None:
        logger.error('MQ is not initialized')
        return

    send_socket.send_string(message)


def init():
    global recv_socket
    global send_socket

    logger = log.logger

    context = zmq.Context()
    recv_socket = context.socket(zmq.SUB)
    recv_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    send_socket = context.socket(zmq.PUB)

    url = f"tcp://*:{config.config['mq_port']}"
    logger.info(f"PUB socket binding to {url}")
    send_socket.bind(url)

    logger.info(f"SUB socket connecting to {url}")
    recv_socket.connect(url)

    logger.info('MQ initialized')
