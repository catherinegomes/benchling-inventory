import logging


def logger():
    logging.basicConfig(format="%(asctime)s - %(levelname)s:%(funcName)s:%(lineno)s '%(message)s'", datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)

    return logger