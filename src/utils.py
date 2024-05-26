import random
import socket


def is_port_in_use(port) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


class StrLen:
    MD5 = 32
    SHA1 = 40
    SHA256 = 64
    SHA512 = 128


def random_hex_string(length: int = StrLen.MD5) -> str:
    # Generate a random hex string of length
    # length: int
    # return: str
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))
