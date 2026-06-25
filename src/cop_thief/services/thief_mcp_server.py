from fastmcp import FastMCP

from cop_thief.shared.config_loader import ConfigLoader


class ThiefMCPServer:
    def __init__(self, config: ConfigLoader):
        self.port = config.get_mcp_ports()["thief_server_port"]
        self.app = FastMCP("thief-server")

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

        # Store for testing
        self._observe = observe

    def start(self) -> None:
        self.app.run(transport="sse", port=self.port, host="0.0.0.0")

    def stop(self) -> None:
        pass
