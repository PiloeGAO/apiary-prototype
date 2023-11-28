"""Routers for the Jobs microservices."""
import json

import httpx
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from apiary_api.models.jobs import (
    JobCreateModel,
    JobEditModel,
    JobModel,
    TaskCreateModel,
    TaskEditModel,
    TaskModel,
    RunCreateModel,
    RunEditModel,
    RunModel,
)
from apiary_api.constants import JOBS_HOSTNAME
from apiary_api import logger
from apiary_api.utils import is_response_successfull

LOGGER = logger.setup()

jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])
runs_router = APIRouter(prefix="/runs", tags=["runs"])


@jobs_router.get("/", response_model=list[JobModel])
async def get_jobs():
    """Get the list of jobs.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/jobs/")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return response.json()


@jobs_router.post("/", response_model=JobModel)
async def post_jobs(job: JobCreateModel):
    """Create a new job.

    Args:
        job (:class:`apiary_api.models.jobs.JobCreateModel`): Job creation data.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Created data or error message.
    """
    async with httpx.AsyncClient() as client:
        tasks_ids = []
        tasks_data = await post_tasks(job.tasks)
        if is_response_successfull(tasks_data):
            tasks_ids.extend([task["id"] for task in json.loads(tasks_data.body)])

        job_data = job.__dict__
        job_data["tasks"] = tasks_ids

        response = await client.post(f"http://{JOBS_HOSTNAME}/jobs/", json=job_data)

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@jobs_router.get("/{job_id}", response_model=JobModel)
async def get_job(job_id: str):
    """Get a job.

    Args:
        id (str): ID of the job.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/jobs/{job_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@jobs_router.patch("/{job_id}", response_model=JobModel)
async def patch_job(job_id: str, job: JobEditModel):
    """Update a job.

    Args:
        id (str): ID of the job.
        job (JobEditModel): Data to update.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Updated data or error message.
    """
    job_response = await get_job(job_id)
    if not is_response_successfull(job_response):
        return job_response

    tasks_ids = []
    for task in job.tasks:
        task_id = task
        if isinstance(task, dict):
            task_id = task["id"]
        tasks_ids.append(task_id)

    job_data = job.__dict__
    job_data["tasks"] = tasks_ids

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://{JOBS_HOSTNAME}/jobs/{job_id}", json=job.__dict__
        )

        if not response.is_success:
            LOGGER.warning("Job update failed.")
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@jobs_router.delete("/{job_id}", response_model=JobModel)
async def delete_job(job_id: str):
    """Delete a job and it's tasks.

    ℹ️: This will also delete the child datas, e.g. Tasks and Runs.

    Args:
        id (str): ID of the job.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Deleted data or error message.
    """
    job_response = await get_job(job_id)
    if not is_response_successfull(job_response):
        return job_response

    job_data = json.loads(job_response.body)
    for task_id in job_data.get("tasks", []):
        task_response = await delete_task(task_id)

        if not is_response_successfull(task_response):
            LOGGER.warning("Task %s deletion failed: %s", task_id, task_response.body)

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://{JOBS_HOSTNAME}/jobs/{job_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@jobs_router.get("/{job_id}/tasks", response_model=list[TaskModel])
async def get_tasks_from_job(job_id: str):
    """Get all the tasks for a job.

    Args:
        job_id (str): ID of the job

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    job_response = await get_job(job_id)
    if not is_response_successfull(job_response):
        return job_response

    job_data = json.loads(job_response.body)

    tasks = []
    for task_id in job_data.get("tasks", []):
        response = await get_task(task_id)

        if not is_response_successfull(response):
            LOGGER.warning("Task %s could not be found.", task_id)
            continue
        tasks.append(json.loads(response.body))

    return JSONResponse(content=tasks)


@jobs_router.post("/{job_id}/tasks", response_model=list[TaskModel])
async def post_tasks_from_job(job_id: str, tasks: list[TaskCreateModel]):
    """Create a list of tasks for a job.

    Args:
        job_id (str): ID of the job
        tasks (list[TaskCreateModel]): Tasks to be created.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Updated data or error message.
    """
    job_edit = JobEditModel()
    tasks_data = await post_tasks(tasks)
    job_edit.tasks = [task["id"] for task in json.loads(tasks_data.body)]
    tasks_from_job = await get_tasks_from_job(job_id)
    job_edit.tasks.extend(
        [
            task["id"]
            for task in json.loads(tasks_from_job.body)
            if not task["id"] in job_edit.tasks
        ]
    )

    await patch_job(job_id, job_edit)
    return tasks_data


@tasks_router.get("/", response_model=list[TaskModel])
async def get_tasks():
    """Get the list of tasks.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/tasks/")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@tasks_router.post("/", response_model=list[TaskModel])
async def post_tasks(tasks: list[TaskCreateModel]):
    """Create a list of tasks.

    Args:
        tasks (list[TaskCreateModel]): Tasks to be created.

    Returns:

        :class:`fastapi.responses.JSONResponse`: Created data.
    """
    tasks_data = []
    async with httpx.AsyncClient() as client:
        for task in tasks:
            task_data = task.__dict__
            response = await client.post(
                f"http://{JOBS_HOSTNAME}/tasks/", json=task_data
            )

            if not response.is_success:
                LOGGER.warning(
                    "Task creation failed with the following message: %s",
                    response.json(),
                )
                continue

            tasks_data.append(response.json())

    return JSONResponse(content=tasks_data)


@tasks_router.get("/{task_id}", response_model=TaskModel)
async def get_task(task_id: str):
    """Get a task.

    Args:
        task_id (str): ID of the task.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/tasks/{task_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@tasks_router.patch("/{task_id}", response_model=TaskModel)
async def patch_task(task_id: str, task: TaskEditModel):
    """Update a task.

    Args:
        task_id (str): ID of the task.
        task (TaskEditModel): Data to update

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Patched data or error message.
    """
    task_response = await get_task(task_id)
    if not is_response_successfull(task_response):
        return task_response

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://{JOBS_HOSTNAME}/tasks/{task_id}", json=task.__dict__
        )

        if not response.is_success:
            LOGGER.warning("Task update failed.")
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@tasks_router.delete("/{task_id}", response_model=TaskModel)
async def delete_task(task_id: str):
    """Delete a task.

    ⚠️: This function do not remove the task from a job but delete the linked data (e.g. Runs).

    Args:
        task_id (str): ID of the task.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Deleted data or error message.
    """
    task_response = await get_task(task_id)
    if not is_response_successfull(task_response):
        return task_response

    task_data = json.loads(task_response.body)
    for run_id in task_data.get("runs", []):
        task_response = await delete_run(run_id)

        if not is_response_successfull(task_response):
            LOGGER.warning("Task %s deletion failed: %s", task_id, task_response.body)

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://{JOBS_HOSTNAME}/tasks/{task_id}")

        if not response.is_success:
            LOGGER.warning(
                "Task deletion failed with the following message: %s", response.content
            )
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@tasks_router.get("/{task_id}/runs", response_model=list[RunModel])
async def get_runs_from_task(task_id: str):
    """Get all the runs for a task.

    Args:
        task_id (str): ID of the task.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    task_response = await get_task(task_id)
    if not is_response_successfull(task_response):
        return task_response

    task_data = json.loads(task_response.body)

    runs = []
    for run_id in task_data.get("runs", []):
        response = await get_run(run_id)

        if not is_response_successfull(response):
            LOGGER.warning("Run %s could not be found.", run_id)
            continue
        runs.append(json.loads(response.body))

    return JSONResponse(content=runs)


@tasks_router.post("/{task_id}/runs", response_model=RunModel)
async def post_run_from_task(task_id: str, run: RunCreateModel):
    """Create a new run for a task.

    Args:
        task_id (str): ID of the task.
        run (RunCreateModel): Run to be created.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Updated data or error message.
    """
    run_response = await post_runs(run)
    if not is_response_successfull(run_response):
        return run_response

    run_data = json.loads(run_response.body)
    runs = [run_data.get("id")]
    runs_data = await get_runs_from_task(task_id)
    runs.extend(json.loads(runs_data.body))

    task_edit = TaskEditModel()
    task_edit.runs = runs

    return await patch_task(task_id, task_edit)


@runs_router.get("", response_model=list[RunModel])
async def get_runs():
    """Get the list of runs.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/runs/")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@runs_router.post("", response_model=RunModel)
async def post_runs(run: RunCreateModel):
    """Create a new run.

    Args:
        run (:class:`apiary_api.models.jobs.RunCreateModel`): Run creation data.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Created data or error message.
    """
    async with httpx.AsyncClient() as client:
        run_data = run.__dict__

        response = await client.post(f"http://{JOBS_HOSTNAME}/runs/", json=run_data)

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@runs_router.get("/{run_id}", response_model=RunModel)
async def get_run(run_id: str):
    """Get a run.

    Args:
        run_id (str): ID of the run.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/runs/{run_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@runs_router.patch("/{run_id}", response_model=RunModel)
async def patch_run(run_id: str, run: RunEditModel):
    """Update a run.

    Args:
        run_id (str): ID of the run.
        run (:class:`apiary_api.models.jobs.RunEditModel`): Run update data.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Created data or error message.
    """
    run_response = await get_task(run_id)
    if not is_response_successfull(run_response):
        return run_response

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://{JOBS_HOSTNAME}/runs/{run_id}", json=run.__dict__
        )

        if not response.is_success:
            LOGGER.warning("Run update failed.")
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@runs_router.delete("/{run_id}", response_model=RunModel)
async def delete_run(run_id: str):
    """Delete a run.

    Args:
        run_id (str): ID of the run.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Deleted data or error message.
    """
    run_response = await get_task(run_id)
    if not is_response_successfull(run_response):
        return run_response

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://{JOBS_HOSTNAME}/runs/{run_id}")

        if not response.is_success:
            LOGGER.warning(
                "Run deletion failed with the following message: %s", response.content
            )
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)
