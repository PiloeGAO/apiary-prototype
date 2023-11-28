"""Submitter configuration singleton."""
import os

import apiary_openapi


class Configuration(object):
    """Submitter configuration class."""

    _instance = None
    config = None

    def __new__(cls, host=""):
        """Return the class singleton.

        Returns:
            object: Configuration singleton.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.config = apiary_openapi.Configuration(
                host=os.environ.get("APIARY_HOST", host)
            )

        if host:
            cls._instance.config.host = host

        return cls._instance

    @property
    def hostname(self):
        """str: Get the hostname for the current configuration."""
        return self.config.host

    @hostname.setter
    def set_hostname(self, hostname):
        """Set the current hostname.

        Args:
            hostname (str): New hostname.
        """
        self.config.host = hostname
