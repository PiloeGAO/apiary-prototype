"""Routers for API statuses."""
import httpx
from fastapi import APIRouter

from apiary_api.constants import JOBS_HOSTNAME
from apiary_api.models import api_status


api_statuses_router = APIRouter(prefix="/api_statuses", tags=["api_statuses"])


@api_statuses_router.get("/", response_model=api_status.APIStatusModel)
async def get_status():
    """Get the status of the main microservice.

    Returns:
        :class:`apiary_api.models.api_status.APIStatusModel`: Microservice datas.
    """
    return api_status.APIStatusModel(
        name="ApiaryAPI microservice",
        description="",
        version="0.0.1",
    )


@api_statuses_router.get("/jobs", response_model=api_status.APIStatusModel)
async def get_jobs_status():
    """Get the status of the jobs microservice.

    Returns:
        :class:`apiary_api.models.api_status.APIStatusModel`: Result from status query.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/status")
    return response.json()
