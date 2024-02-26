"""Manager class for the worker."""
import re
import threading
import json
import platform

import websocket


class WorkerManager:
    def __init__(self, url, retry=3) -> None:
        _, self.secure, self.host = WorkerManager.get_url_data(url)

        if self.secure:
            raise RuntimeError("Secure connections not supported.")

        self.ws_connection = websocket.WebSocketApp(
            f"ws://{self.host}/workers/ws",
            on_open = lambda ws : self.on_open(ws),
            on_message = lambda ws, msg : self.on_message(ws, msg),
            on_error = lambda ws, msg : self.on_error(ws, msg),
            on_close = lambda ws, status, msg : self.on_close(ws, status, msg),
            header={
                "WORKER_NAME": platform.node(),
                "DEFAULT_POOLS": json.dumps([]),
                "DEFAULT_TAGS": json.dumps([]),
            }
        )
        self.connection_status = False
        threading.Thread(target=self.ws_connection.run_forever).start()

    @classmethod
    def get_url_data(cls, url):
        """Get the protocol, secure state and host root from an url.

        Args:
            url (str): HTTP/HTTPS/WS/WSS url.

        Returns:
            tuple[str]: The protocol, secure state and host root.
        """
        matches = re.match(r"(?P<protocol>http|ws)(?P<secure>s?)://(?P<url>.*)/", url)
        elements = matches.groupdict()
        return (
            elements.get("protocol", "http"),
            True if elements.get("secure", None) else False,
            elements.get("url", "127.0.0.1")
        )

    def on_open(self, ws):
        self.connection_status = True

    def on_message(self, ws, message):
        print(f"Message: {message}")

    def on_error(self, ws, message):
        print(f"Error: {message}")

    def on_close(self, ws, status, message):
        self.connection_status = False
        print(status, message)
