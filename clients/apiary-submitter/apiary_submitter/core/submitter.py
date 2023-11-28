"""Submitter class description."""
import apiary_openapi
from apiary_openapi.models.job_create_model import JobCreateModel
from apiary_openapi.models.job_edit_model import JobEditModel
from apiary_openapi.models.task_create_model import TaskCreateModel

from apiary_submitter.core.configuration import Configuration
from apiary_submitter.core.job import Job
from apiary_submitter.core.statuses import Statuses
from apiary_submitter.exceptions import SubmitException, RequestException
from apiary_submitter import logger

LOGGER = logger.setup()


# TODO: Move the submit outside of this to `Job.submit()` and store response in them.
class Submitter:
    """Submitter class."""

    def __init__(self, host="http://localhost") -> None:
        configuration_object = Configuration(host=host)
        self.configuration = configuration_object.config

        self.statuses = Statuses()

    def submit(self, job: Job) -> str:
        """Submit a job to the farm.

        Args:
            job (:class:`apiary_submitter.core.job.Job`): Job to be send.

        Raises:
            :class:`apiary_submitter.exceptions.SubmitException`:
                Job creation failed.

        Returns:
            str: Job id.
        """
        try:
            job_status = self.statuses.job["WAITING"]
        except RequestException as error:
            raise SubmitException(f"Fetching jobs statuses failed ({error})") from error

        with apiary_openapi.ApiClient(self.configuration) as api_client:
            api_instance = apiary_openapi.JobsApi(api_client)
            job_model = JobCreateModel(
                name=job.name,
                user_id=0,
                status=job_status,
                pools=job.pools,
                priority=job.priority,
                tags=job.tags,
                metadata=job.metadata,
            )

            try:
                response = api_instance.post_jobs_jobs_post(job_model)
            except Exception as error:
                raise SubmitException(f"Job creation failed: {error}") from error

            job_response = response.to_dict()

        tasks = {}
        try:
            task_status = self.statuses.task["READY"]
        except RequestException as error:
            self.job_invalidation(job_response.get("id"))
            raise SubmitException(
                f"Fetching tasks statuses failed ({error})"
            ) from error

        for task in job.all_tasks:
            parents = [
                tasks.get(parent_task, None)
                for parent_task in job.tasks
                if task in parent_task.childrens
            ]

            if None in parents:
                LOGGER.warning(
                    "Some parent tasks are not available online, skipping linking to them."
                )

            with apiary_openapi.ApiClient(self.configuration) as api_client:
                api_instance = apiary_openapi.JobsApi(api_client)

                task_model = TaskCreateModel(
                    name=task.name,
                    command=task.command,
                    status=task_status,
                    parents=[
                        parent.get("id") for parent in parents if parent is not None
                    ],
                    tags=task.tags,
                    metadata=task.metadata,
                )

                try:
                    response = api_instance.post_tasks_from_job_jobs_job_id_tasks_post(
                        job_response.get("id"), [task_model]
                    )
                except Exception as error:
                    self.job_invalidation(job_response.get("id"))
                    raise SubmitException(f"Task creation failed: {error}") from error

                task_response = response[0]
                tasks[task] = task_response.to_dict()

        return job_response.get("id", None)

    def job_invalidation(self, job_id):
        """Invalidate a job when task creation failed.

        Args:
            job_id (str): Job ID.

        Raises:
            SubmitException: Job invalidation failed.
        """
        with apiary_openapi.ApiClient(self.configuration) as api_client:
            api_instance = apiary_openapi.JobsApi(api_client)
            job_model = JobEditModel(status=self.statuses.job["ERROR"])

            try:
                _ = api_instance.patch_job_jobs_job_id_patch(job_id, job_model)
            except Exception as error:
                raise SubmitException(f"Job invalidation failed: {error}") from error

        LOGGER.info("Job invalidation successfully.")
        return
