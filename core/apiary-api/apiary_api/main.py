"""Main Apiary API package file."""
import httpx
from fastapi import FastAPI

from apiary_api.models import status
from apiary_api.routers import jobs
from apiary_api.constants import JOBS_HOSTNAME
from apiary_api import logger

LOGGER = logger.setup()

app = FastAPI(
    title="ApiaryAPI",
    description="",
    version="0.1.0",
    servers=[
        {"url": "http://localhost", "description": "Local developement server."},
    ],
    license_info={
        "name": "MIT License",
        "identifier": "MIT",
    },
)
app.include_router(jobs.jobs_router)
app.include_router(jobs.tasks_router)
app.include_router(jobs.runs_router)

@app.get("/")
def read_root():
    """Demo endpoint.

    Returns:
        dict: Hello world dict.
    """
    return {"Hello": "World"}

@app.get("/status", tags=["statuses"], response_model=status.StatusModel)
async def get_status():
    """Get the status of the microservice.

    Returns:
        dict: Microservice datas.
    """
    return status.StatusModel(
        name="ApiaryAPI microservice",
        description="",
        version="0.0.1",
    )

@app.get("/status/jobs", tags=["statuses"], response_model=status.StatusModel)
async def get_jobs_status():
    """Get the status of the jobs microservice.

    Returns:
        dict: Result from status query.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/status")
    return response.json()
