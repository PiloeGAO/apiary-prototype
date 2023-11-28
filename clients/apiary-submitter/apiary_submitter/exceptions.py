"""List of all the exceptions for the module."""


class SubmitException(Exception):
    """Exception to be raised when the submit failed."""


class RequestException(Exception):
    """Exception to be raised when a query to the API failed."""
