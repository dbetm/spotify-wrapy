import logging
import sys


def load_logger(name: str = "wrapy"):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    return logging.getLogger(name=name)
