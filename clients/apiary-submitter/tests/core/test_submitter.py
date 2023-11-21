"""Testing the :class:`apiary_submitter.core.submitter.Submitter`"""
import os

import pytest

import apiary_openapi

from apiary_submitter.core.job import Job
from apiary_submitter.core.task import Task
from apiary_submitter.core.submitter import Submitter
from apiary_submitter.exceptions import SubmitException


@pytest.fixture
def api_submit_status():
    """Check if we are doing API calls or only mocked unit tests.

    Returns:
        bool: Submit status.
    """
    return os.environ.get("API_CALLS", True)


@pytest.fixture
def job():
    """Job generator for testing.

    Returns:
        :class:`apiary_submitter.core.job.Job`: A job with tasks.
    """
    parent_task = Task("echo 1")
    inter_task = Task("echo 2")
    parent_task.add_child(inter_task)
    child_task = Task("echo 3")
    parent_task.add_child(child_task)
    inter_task.add_child(child_task)

    demo_job = Job(
        name="Submitter Tester",
        priority=750,
        tasks=[parent_task],
        pools=["demo"],
        tags=["tests"],
        metadata={"hello": "world"},
    )
    return demo_job


def test_submit(api_submit_status, job):  # pylint: disable=redefined-outer-name
    """Test a job submission to the API.

    Args:
        api_submit_status (bool): Allow the test if api calls is supported.
        job (:class:`apiary_submitter.core.job.Job`): A demo job.
    """
    if not api_submit_status:
        pytest.skip("API calls tests are not supported.")

    submitter = Submitter(host=os.environ.get("API_HOST", "http://localhost"))
    job_id = submitter.submit(job)

    assert isinstance(job_id, str)

    configuration = apiary_openapi.Configuration(host="http://localhost")
    with apiary_openapi.ApiClient(configuration) as api_client:
        api_instance = apiary_openapi.JobsApi(api_client)
        response = api_instance.get_job_jobs_job_id_get(job_id)

    assert response != {}


def test_submit_failed(job):  # pylint: disable=redefined-outer-name
    """Test a failing job submission.

    Args:
        job (:class:`apiary_submitter.core.job.Job`): A demo job.
    """
    submitter = Submitter(host="http://not-a-valid-api.local")

    with pytest.raises(SubmitException):
        submitter.submit(job)


def test_submit_mocked(job):  # pylint: disable=redefined-outer-name
    """Test a mocked job submission to the API.

    Args:
        job (:class:`apiary_submitter.core.job.Job`): A demo job.
    """
    assert True
