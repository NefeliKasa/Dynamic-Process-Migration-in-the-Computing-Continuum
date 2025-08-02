import logging


def setup_logger(name=__name__):
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s | %(asctime)s | %(message)s",
    )
    return logging.getLogger(name)
