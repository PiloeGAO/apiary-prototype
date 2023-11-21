"""Utility functions for logging to console."""
from functools import cache
import logging
import os


@cache
def setup():
    """Setup the package logger.

    Returns:
        :class:`logging.Logger`: Logger object.
    """
    logger = logging.getLogger("apiary_submitter")

    if os.getenv("APIARY_SUBMITTER_DEBUG"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Console logging.
    formatter = logging.Formatter(
        "Apiary Submitter | %(levelname)s - %(message)s @ [%(asctime)s] | %(pathname)s:%(lineno)d",
        "%y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
