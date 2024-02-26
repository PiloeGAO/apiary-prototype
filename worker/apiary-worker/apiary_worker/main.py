"""Main module entrypoint."""
import websocket

from apiary_worker.manager import WorkerManager

if __name__ == "__main__":
    websocket.enableTrace(True)
    WorkerManager("http://localhost/")
