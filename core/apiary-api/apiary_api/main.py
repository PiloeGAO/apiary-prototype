"""Main Apiary API package file."""
import os

import httpx
from fastapi import FastAPI

from apiary_api.constants import JOBS_HOSTNAME

app = FastAPI()

@app.get("/")
def read_root():
    """Demo endpoint.

    Returns:
        dict: Hello world dict.
    """
    return {"Hello": "World"}

@app.get("/status")
async def get_status():
    """Get the status of the microservice.

    Returns:
        dict: Microservice datas.
    """
    return {
        "name": "ApiaryAPI microservice",
        "version": "0.0.1",
    }

@app.get("/status/jobs")
async def get_jobs_status():
    """Get the status of the jobs microservice.

    Returns:
        dict: Result from status query.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{JOBS_HOSTNAME}/status")
    return response.json()
