import logging
from io import StringIO


def setup_logger() -> tuple[logging.Logger, StringIO]:
    logger = logging.getLogger("packer_deployment_logger")
    logger.setLevel(logging.DEBUG)
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    return logger, log_stream
