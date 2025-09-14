import uuid

import httpx

from ..config import ToolkitConfig
from ..utils import get_logger
from .base import AsyncBaseToolkit, register_tool

logger = get_logger(__name__)


class BashRemoteToolkit(AsyncBaseToolkit):
    """Wrap the built-in remote shell service.
    Usage of API: /api/create_terminal; /api/execute; /api/close_server
    """

    def __init__(self, config: ToolkitConfig = None) -> None:
        super().__init__(config)
        self.server_url = self.config.config.get("server_url")
        self.headers = {"X-API-Key": self.config.config.get("server_key")}
        # NOTE: you should manually manage your session_id, non-duplicate!
        self.session_info = None
        self.session_id = f"utu-{uuid.uuid4()}"

    async def build(self):
        # call /api/create_terminal
        logger.info(f"starting terminal with session_id: {self.session_id}")
        with httpx.Client() as client:
            data = {"session_id": self.session_id}
            response = client.post(f"{self.server_url}/api/create_terminal", headers=self.headers, json=data)
        assert response.status_code == 200, response.text
        data = response.json()
        self.session_info = data
        logger.info(f"session info: {data}")
        return data

    async def cleanup(self):
        # call /api/close_server
        logger.info(f"closing terminal with session_id: {self.session_id}")
        with httpx.Client() as client:
            data = {"session_id": self.session_id}  # can automatically close the server with the session_id
            response = client.post(f"{self.server_url}/api/close_server", headers=self.headers, json=data)
        if not (response.status_code == 200):
            logger.info(f"Failed to close terminal with session_info: {self.session_info}")

    @register_tool
    async def exec(self, cmd: str) -> str:
        """Execute a command in the terminal.

        Args:
            cmd: The command to execute
        """
        assert self.session_info is not None, "Session not started!"
        logger.info(f"executing command: {cmd}")
        with httpx.Client(timeout=httpx.Timeout(60)) as client:
            # FIXME: handle timeout error
            data = {"session_id": self.session_id, "command": cmd}
            response = client.post(f"{self.server_url}/api/execute", headers=self.headers, json=data)
        assert response.status_code == 200, response.text
        data = response.json()
        return str(
            {
                "execution_time": round(data["execution_time"], 2),
                "output": data["output"],
            }
        )
