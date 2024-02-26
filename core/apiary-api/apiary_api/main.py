"""Main Apiary API package file."""
from fastapi import FastAPI

from apiary_api.routers import jobs, statuses, api_statuses, workers
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

app.include_router(api_statuses.api_statuses_router)
app.include_router(jobs.jobs_router)
app.include_router(jobs.tasks_router)
app.include_router(jobs.runs_router)
app.include_router(statuses.statuses_router)
app.include_router(workers.workers_router)
