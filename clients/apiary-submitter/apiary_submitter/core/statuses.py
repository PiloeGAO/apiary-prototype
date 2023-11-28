"""Singleton storing the statuses for all the entities."""
import json

import apiary_openapi

from apiary_submitter.core.configuration import Configuration
from apiary_submitter.exceptions import RequestException


class Statuses(object):
    """Statuses storage.

    We store statuses in a singleton since they are constants and require to be fetched once.
    """

    _instance = None

    _job = None
    _task = None

    def __new__(cls):
        """Get the class singleton.

        Returns:
            object: Statuses singleton.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def job(self):
        """Get all the jobs statuses.

        Raises:
            :class:`apiary_submitter.exceptions.RequestException`:
                Could not fetch statuses for jobs.

        Returns:
            dict: Jobs statuses with their matching IDs.
        """
        if not self._job:
            configuration_object = Configuration()
            with apiary_openapi.ApiClient(configuration_object.config) as api_client:
                api_instance = apiary_openapi.StatusesApi(api_client)
                try:
                    response = (
                        api_instance.get_jobs_statuses_status_jobs_get_without_preload_content()
                    )
                except Exception as error:
                    raise RequestException(
                        f"Could not fetch statuses for jobs ({error})"
                    ) from error

                if not response:
                    raise RequestException(
                        "Could not fetch statuses for jobs (empty response)"
                    )

                self._job = json.loads(response.read())

        return self._job

    @property
    def task(self):
        """Get all the tasks statuses.

        Raises:
            :class:`apiary_submitter.exceptions.RequestException`:
                Could not fetch statuses for tasks.

        Returns:
            dict: Tasks statuses with their matching IDs.
        """
        if not self._task:
            configuration_object = Configuration()
            with apiary_openapi.ApiClient(configuration_object.config) as api_client:
                api_instance = apiary_openapi.StatusesApi(api_client)
                try:
                    response = (
                        api_instance.get_tasks_statuses_status_tasks_get_without_preload_content()
                    )
                except Exception as error:
                    raise RequestException(
                        f"Could not fetch statuses for tasks ({error})"
                    ) from error

                if not response:
                    raise RequestException(
                        "Could not fetch statuses for tasks (empty response)"
                    )

                self._task = json.loads(response.read())

        return self._task
