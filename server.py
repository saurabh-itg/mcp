from mcp.server.fastmcp import FastMCP
import os

# 1. Initialize FastMCP instead of the base Server class
mcp = FastMCP("file-assistant")

# 2. Use the .tool() decorator from the mcp instance
@mcp.tool()
def list_files(directory: str = ".") -> str: # Added a default
    """List all files in a directory. Returns a formatted string of filenames."""
    try:
        # 1. Expand paths
        target_path = os.path.abspath(os.path.expanduser(directory))
        
        # 2. Get the list
        files = os.listdir(target_path)
        
        # 3. Return a clean string (LLMs handle strings better than raw lists sometimes)
        if not files:
            return f"The directory '{target_path}' is empty."
            
        return f"Files in {target_path}:\n- " + "\n- ".join(files)
    except Exception as e:
        return f"Error reading directory: {str(e)}"

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
