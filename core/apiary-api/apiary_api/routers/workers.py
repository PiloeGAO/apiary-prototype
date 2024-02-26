"""Routers for the Workers microservices."""
import httpx
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from apiary_api.core.workers import WorkersConnectionManager
from apiary_api.models.workers import WorkersModel, WorkersEditModel
from apiary_api.constants import WORKERS_HOSTNAME
from apiary_api import logger
from apiary_api.utils import is_response_successfull

LOGGER = logger.setup()

workers_router = APIRouter(prefix="/workers", tags=["workers"])
workers_clients_manager = WorkersConnectionManager()

@workers_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Websocket endpoint for workers, used to create a bi-directionnal connection with the API.

    Args:
        websocket (:class:`fastapi.WebSocket`): Websocket connection.
    """
    await workers_clients_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            LOGGER.info("Got WS data: %s", data)
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        workers_clients_manager.disconnect(websocket)


@workers_router.get("/", response_model=list[WorkersModel])
async def get_workers():
    """Get the list of workers.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{WORKERS_HOSTNAME}/workers/")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return response.json()


@workers_router.get("/connected")
async def get_connected_workers():
    """Return a list of connected workers.

    Returns:
        list[WebSocket]: List of connected websocket instances.
    """
    return workers_clients_manager.active_connections


@workers_router.get("/{worker_id}", response_model=WorkersModel)
async def get_worker(worker_id: str):
    """Get a worker.

    Args:
        id (str): ID of the worker.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Fetched data or error message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{WORKERS_HOSTNAME}/workers/{worker_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@workers_router.patch("/{worker_id}", response_model=WorkersModel)
async def patch_worker(worker_id: str, worker: WorkersEditModel):
    """Update a worker.

    Args:
        id (str): ID of the worker.
        worker (WorkersEditModel): Data to update.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Updated data or error message.
    """
    worker_response = await get_worker(worker_id)
    if not is_response_successfull(worker_response):
        return worker_response

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://{WORKERS_HOSTNAME}/workers/{worker_id}", json=worker.__dict__
        )

        if not response.is_success:
            LOGGER.warning("Worker update failed.")
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@workers_router.delete("/{worker_id}", response_model=WorkersModel)
async def delete_worker(worker_id: str):
    """Delete a worker.

    Args:
        id (str): ID of the worker.

    Returns:
        :class:`fastapi.responses.JSONResponse` or :class:`fastapi.Response`:
            Deleted data or error message.
    """
    # TODO: Mark all runs from this worker with an invalid ID (ex: None).
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://{WORKERS_HOSTNAME}/workers/{worker_id}")

        if not response.is_success:
            return Response(content=response.content, status_code=response.status_code)

    return JSONResponse(content=response.json(), status_code=response.status_code)
