"""Utility functions for logging to console."""
from functools import cache
import logging

from apiary_api.constants import DEBUG

@cache
def setup():
    """Setup the package logger.

    Returns:
        :class:`logging.Logger`: Logger object.
    """
    logger = logging.getLogger("apiary_api")

    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Console logging.
    formatter = logging.Formatter(
        "Apiary API | %(levelname)s - %(message)s @ [%(asctime)s] | %(pathname)s:%(lineno)d",
        "%y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
