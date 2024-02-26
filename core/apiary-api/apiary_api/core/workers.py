"""Web Socket connection manager."""
from datetime import datetime

from fastapi import WebSocket
import httpx

from apiary_api import logger
from apiary_api.constants import WORKERS_HOSTNAME

LOGGER = logger.setup()


async def create_worker(name, ip, pools, tags):
    worker_data = {
        "name": name,
        "ip": ip,
        "status": 0,
        "last_connection": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pools": pools,
        "tags": tags,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://{WORKERS_HOSTNAME}/workers/", json=worker_data)

        if not response.is_success:
            return None

    return response.json()


async def get_worker_by_name(name):
    workers = None
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{WORKERS_HOSTNAME}/workers/")

        if not response.is_success:
            return None

        workers = response.json()

    LOGGER.info(workers)
    return None




class WorkersConnectionManager:
    """WebSocket connection manager class.
    """
    def __init__(self) -> None:
        """Class initializer.
        """
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Connect client.

        Args:
            websocket (:class:`fastapi.WebSocket`): Websocket connection.
        """
        await websocket.accept()
        LOGGER.info("New worker connected: %s", websocket.client)
        worker = await get_worker_by_name(
            websocket.headers.get("WORKER_NAME") or websocket.client.host
        )

        if not worker:
            worker = await create_worker(
                websocket.headers.get("WORKER_NAME", websocket.client.host),
                websocket.client.host,
                websocket.headers.get("DEFAULT_POOLS"),
                websocket.headers.get("DEFAULT_TAGS"),
            )

        LOGGER.info(worker)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Disconnect client.

        Args:
            websocket (:class:`fastapi.WebSocket`): Websocket connection.
        """
        self.active_connections.remove(websocket)

    async def send_message(self, data: dict, websocket: WebSocket):
        """Send a direct message to the client.

        Args:
            data (dict): Data to send.
            websocket (:class:`fastapi.WebSocket`): Websocket connection.
        """
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        """Broadcast a message to all the clients.

        Args:
            data (dict): Data to send.
        """
        for connection in self.active_connections:
            await connection.send_json(data)
