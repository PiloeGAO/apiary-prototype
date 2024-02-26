"""Apiary Workers package file."""
from typing import Optional
from fastapi import FastAPI
from pydantic import Field
from fastapi_crudrouter_mongodb import CRUDRouter, MongoModel, MongoObjectId
import motor.motor_asyncio

from apiary_workers.constants import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

# DB Setup.
db_client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
)
db = db_client.jobs

# DB Models.
class WorkerModel(MongoModel):
    """Worker model"""
    id: Optional[MongoObjectId] = Field()
    name: Optional[str]
    ip: Optional[str]
    status: Optional[int] = 0
    last_connection: Optional[str] = ""
    pools: Optional[list[str]] = []
    tags: Optional[list[str]] = []
    metadata: Optional[dict] = {}

# FastAPI app.
app = FastAPI()

workers_controller = CRUDRouter(
    model=WorkerModel,
    db=db,
    collection_name="workers",
    prefix="/workers",
    tags=["workers"],
)
app.include_router(workers_controller)

@app.get("/status")
async def get_status():
    """Get the status of the microservice.

    Returns:
        dict: Microservice datas.
    """
    return {
        "name": "ApiaryWorkers microservice",
        "description": "",
        "version": "0.0.1",
    }
