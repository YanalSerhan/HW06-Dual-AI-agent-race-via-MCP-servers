from fastmcp import FastMCP

from cop_thief.shared.config_loader import ConfigLoader

import os
from fastmcp.server.auth import StaticTokenVerifier

class ThiefMCPServer:
    def __init__(self, config: ConfigLoader):
        self.port = config.get_mcp_ports()["thief_server_port"]
        
        token = os.environ.get("MCP_AUTH_TOKEN")
        auth = None
        if token:
            auth = StaticTokenVerifier({token: {"client_id": "thief-client"}})
            
        self.app = FastMCP("thief-server", auth=auth)

        @self.app.tool()
        def move(direction: str) -> str:
            """Move the thief in a direction."""
            valid = [
                "up", "down", "left", "right",
                "up-left", "up-right", "down-left", "down-right"
            ]
            if direction not in valid:
                return "Invalid direction"
            return f"Thief moved {direction}"

        @self.app.tool()
        def observe() -> str:
            """Observe the environment."""
            return (
                "You are in the lower-right area. The cop is 2 steps to your north. "
                "There is a barrier blocking west."
            )

        @self.app.tool()
        def get_valid_moves() -> list[str]:
            """Get valid moves."""
            return ["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"]

        @self.app.tool()
        def reset_game(cop_x: int, cop_y: int, thief_x: int, thief_y: int) -> str:
            return "Game reset"

        @self.app.tool()
        def receive_message(message: str) -> str:
            return f"Received: {message}"

        @self.app.tool()
        def update_state(
            cop_x: int,
            cop_y: int,
            thief_x: int,
            thief_y: int,
            barriers: list[dict[str, int]] | None = None,
            cop_barriers_left: int = 5,
            turn_index: int = 0,
            captured: bool = False,
        ) -> str:
            return "State updated"

        @self.app.tool()
        def choose_action() -> dict[str, str]:
            return {
                "move": "n",
                "message": "some message"
            }

        # Store for testing
        self._observe = observe

    def start(self) -> None:
        import typing
        transport = typing.cast(typing.Literal["http", "sse", "stdio", "streamable-http"], os.environ.get("MCP_TRANSPORT", "streamable-http"))
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        
        # Ensure correct public URL resolution behind Render proxy
        uv_config = {"proxy_headers": True, "forwarded_allow_ips": "*"}
        
        self.app.run(
            transport=transport, 
            port=self.port, 
            host=host, 
            path="/mcp",
            uvicorn_config=uv_config
        )

    def stop(self) -> None:
        pass
