from fastmcp import FastMCP

from cop_thief.shared.config_loader import ConfigLoader

import os
from fastmcp.server.auth import StaticTokenVerifier

class CopMCPServer:
    def __init__(self, config: ConfigLoader):
        self.port = config.get_mcp_ports()["cop_server_port"]
        
        token = os.environ.get("MCP_AUTH_TOKEN")
        auth = None
        if token:
            auth = StaticTokenVerifier({token: {"client_id": "cop-client"}})
            
        self.app = FastMCP("cop-server", auth=auth)

        self.state = {"pos": (0, 0), "barriers": 5}

        @self.app.tool()
        def move(direction: str) -> str:
            """Move the cop in a direction."""
            valid = [
                "up", "down", "left", "right",
                "up-left", "up-right", "down-left", "down-right"
            ]
            if direction not in valid:
                return "Invalid direction"
            return f"Cop moved {direction}"

        @self.app.tool()
        def place_barrier() -> str:
            """Place a barrier."""
            if self.state["barriers"] > 0:
                self.state["barriers"] -= 1
                return f"Barrier placed at {self.state['pos']}"
            return "No barriers remaining"

        @self.app.tool()
        def observe() -> str:
            """Observe the environment."""
            return (
                "You are in the upper-left area. The thief is 3 steps to your east. "
                f"You have {self.state['barriers']} barriers remaining."
            )

        @self.app.tool()
        def get_valid_moves() -> list[str]:
            """Get valid moves."""
            return ["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"]

        @self.app.tool()
        def get_deterministic_move(
            current_row: int, current_col: int, 
            opponent_row: int, opponent_col: int,
            barriers_remaining: int,
            valid_moves: list[str]
        ) -> str:
            """Get the next deterministic move for the cop based on WallBuilder logic."""
            from cop_thief.services.wall_builder import WallBuilder
            if not hasattr(self, "wall_builder"):
                self.wall_builder = WallBuilder()
            current_pos = (current_row, current_col)
            opponent_pos = (opponent_row, opponent_col)
            action = self.wall_builder.next_action(
                current_pos=current_pos,
                valid_moves=valid_moves,
                barriers_remaining=barriers_remaining,
                opponent_pos=opponent_pos
            )
            return action

        # Store for testing
        self._observe = observe
        self._get_valid_moves = get_valid_moves

    def start(self) -> None:
        self.app.run(transport="sse", port=self.port, host="0.0.0.0", path="/mcp")

    def stop(self) -> None:
        pass
