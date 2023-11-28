"""Routers for the statuses."""
from functools import cache

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from apiary_api.core import statuses


statuses_router = APIRouter(prefix="/status", tags=["statuses"])


@cache
@statuses_router.get("/jobs")
async def get_jobs_statuses():
    """List all the jobs statuses.

    Returns:
        dict: List of all the statuses.
    """
    return JSONResponse(content=statuses.JobStatuses.to_dict())


@cache
@statuses_router.get("/tasks")
async def get_tasks_statuses():
    """List all the tasks statuses.

    Returns:
        dict: List of all the statuses.
    """
    return JSONResponse(content=statuses.TaskStatuses.to_dict())


@cache
@statuses_router.get("/runs")
async def get_runs_statuses():
    """List all the runs statuses.

    Returns:
        dict: List of all the statuses.
    """
    return JSONResponse(content=statuses.RunStatuses.to_dict())
