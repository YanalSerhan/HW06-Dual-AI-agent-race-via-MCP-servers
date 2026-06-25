import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cop_thief.shared.config_loader import ConfigLoader

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_mcp_server.py [cop|thief]")
        sys.exit(1)
        
    role = sys.argv[1].lower()
    config = ConfigLoader("config/config.json")
    config.load()
    
    # Render sets the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    if role == "cop":
        from cop_thief.services.cop_mcp_server import CopMCPServer
        server = CopMCPServer(config)
        server.port = port
        print(f"Starting Cop MCP Server on port {port}...")
        server.start()
    elif role == "thief":
        from cop_thief.services.thief_mcp_server import ThiefMCPServer
        server = ThiefMCPServer(config)
        server.port = port
        print(f"Starting Thief MCP Server on port {port}...")
        server.start()
    else:
        print(f"Unknown role: {role}")
        sys.exit(1)

if __name__ == "__main__":
    main()
