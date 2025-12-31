import os
import subprocess
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("masscan-mcp")


@mcp.tool()
def do_masscan(target: str, port: str, masscan_args: list[str] = None) -> str:
    """
    Run masscan with specified target. MASSCAN is a fast port scanner.
    The primary input parameters are the IP addresses/ranges you want to scan, and the port numbers.

    Args:
        target: Target information. Example: 1.1.1.1 or 10.0.0.0/8
        port: Target port. Example: 1234 or 0-65535
        masscan_args: Additional masscan arguments like --max-rate
    """
    # Build command arguments - use sudo for raw packet access
    cmd = ["sudo", "masscan", "-p" + port, target]
    
    if masscan_args:
        cmd.extend(masscan_args)
    
    try:
        # Run masscan with sudo
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return output + "\n\nmasscan completed successfully"
        else:
            return f"masscan exited with code {result.returncode}\n\nOutput:\n{output}"
            
    except subprocess.TimeoutExpired:
        return "masscan timed out after 5 minutes"
    except FileNotFoundError:
        return "Error: masscan binary not found. Please ensure masscan is installed."
    except Exception as e:
        return f"Failed to run masscan: {str(e)}"


# Run the server with HTTP transport
if __name__ == "__main__":
    # Get host and port from environment (Render sets PORT automatically)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        path="/mcp"
    )
