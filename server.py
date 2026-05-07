from mcp.server.fastmcp import FastMCP
import os

# 1. Initialize FastMCP instead of the base Server class
mcp = FastMCP("file-assistant")

# 2. Use the .tool() decorator from the mcp instance
@mcp.tool()
def list_files(directory: str) -> list:
    """List all files in a directory"""
    try:
        # Expand user paths (like ~) for better usability
        path = os.path.expanduser(directory)
        return os.listdir(path)
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def read_file(path: str) -> str:
    """Read contents of a file"""
    try:
        full_path = os.path.expanduser(path)
        with open(full_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # 3. This starts the server via stdio by default
    mcp.run()
