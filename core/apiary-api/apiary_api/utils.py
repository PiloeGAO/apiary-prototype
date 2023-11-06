"""Utility functions used in the main API."""

from fastapi import Response

def is_response_successfull(response: Response):
    """Response are sucessfull for codes between 200 and 299.

    Args:
        response (Response): FastAPI response.

    Returns:
        bool: `True` if the response status code is between 200 and 299, `False` otherwise.
    """
    if response.status_code < 200 and response.status_code >= 300:
        return False
    return True
