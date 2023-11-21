"""Apiary Jobs package file."""
from datetime import datetime

from typing import Optional
from fastapi import FastAPI
from pydantic import Field
from fastapi_crudrouter_mongodb import CRUDRouter, MongoModel, MongoObjectId
import motor.motor_asyncio

from apiary_jobs.constants import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

# DB Setup.
db_client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
)
db = db_client.jobs

# DB Models.
class RunModel(MongoModel):
    """Run model."""
    id: Optional[MongoObjectId] = Field()
    date: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status: Optional[int] = 0
    worker_id: Optional[int]
    log: Optional[list[str]]
    command: Optional[str]
    metadata: Optional[dict] = {}

class TaskModel(MongoModel):
    """Task model."""
    id: Optional[MongoObjectId] = Field()
    name: Optional[str]
    command: Optional[str]
    status: Optional[int] = 0
    parents: Optional[list[MongoObjectId]] = []
    tags: Optional[list[str]] = []
    runs: Optional[list[MongoObjectId]] = []
    metadata: Optional[dict] = {}

class JobModel(MongoModel):
    """Job model"""
    id: Optional[MongoObjectId] = Field()
    name: Optional[str]
    user_id: Optional[int]
    submission: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status: Optional[int] = 0
    pools: Optional[list[str]] = []
    priority: Optional[int] = 500
    tasks: Optional[list[MongoObjectId]] = []
    tags: Optional[list[str]] = []
    metadata: Optional[dict] = {}

# FastAPI app.
app = FastAPI()

jobs_controller = CRUDRouter(
    model=JobModel,
    db=db,
    collection_name="jobs",
    prefix="/jobs",
    tags=["jobs"],
)
app.include_router(jobs_controller)

tasks_controller = CRUDRouter(
    model=TaskModel,
    db=db,
    collection_name="tasks",
    prefix="/tasks",
    tags=["tasks"],
)
app.include_router(tasks_controller)

runs_controller = CRUDRouter(
    model=RunModel,
    db=db,
    collection_name="runs",
    prefix="/runs",
    tags=["runs"],
)
app.include_router(runs_controller)

@app.get("/status")
async def get_status():
    """Get the status of the microservice.

    Returns:
        dict: Microservice datas.
    """
    return {
        "name": "ApiaryJobs microservice",
        "description": "",
        "version": "0.0.1",
    }
