import os
import subprocess
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("masscan-mcp")

# Note about platform limitations
PLATFORM_NOTE = """
⚠️ PLATFORM LIMITATION: Masscan requires CAP_NET_RAW capability to send raw network packets.
Cloud container platforms like Render.com do not allow this capability for security reasons.

To actually run masscan, you need to execute the command on a system where you have:
- Root/sudo access, OR
- Docker with --cap-add=NET_RAW flag, OR
- A VPS/dedicated server with raw socket permissions

The command below should be run on your local machine or authorized server.
"""


@mcp.tool()
def do_masscan(target: str, port: str, masscan_args: list[str] = None) -> str:
    """
    Run masscan with specified target. MASSCAN is a fast port scanner.
    The primary input parameters are the IP addresses/ranges you want to scan, and the port numbers.
    
    NOTE: Due to cloud platform security restrictions, this tool generates the command
    for you to run locally. Masscan requires raw socket access (CAP_NET_RAW) which is
    not available on containerized cloud platforms like Render.

    Args:
        target: Target information. Example: 1.1.1.1 or 10.0.0.0/8
        port: Target port. Example: 1234 or 0-65535
        masscan_args: Additional masscan arguments like --max-rate
    """
    # Build command arguments
    cmd = ["masscan", "-p" + port, target]
    
    if masscan_args:
        cmd.extend(masscan_args)
    
    command_string = " ".join(cmd)
    
    # First, try to run it (in case the platform does support it)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout + result.stderr
        
        # Check if we got the permission denied error
        if "permission denied" in output.lower() or "need to sudo" in output.lower():
            return f"""
{PLATFORM_NOTE}

📋 Command to run locally:
sudo {command_string}

Or with Docker (if you have Docker installed):
docker run --rm --cap-add=NET_RAW masscan/masscan -p{port} {target}

💡 Tip: Install masscan on your local machine:
- macOS: brew install masscan
- Ubuntu/Debian: sudo apt-get install masscan
- From source: https://github.com/robertdavidgraham/masscan
"""
        
        if result.returncode == 0:
            return f"✅ Scan completed successfully!\n\nResults:\n{output}"
        else:
            return f"masscan exited with code {result.returncode}\n\nOutput:\n{output}"
            
    except subprocess.TimeoutExpired:
        return "masscan timed out after 5 minutes"
    except FileNotFoundError:
        return f"""
Error: masscan binary not found in this container.

📋 Command to run locally:
sudo {command_string}

💡 Install masscan:
- macOS: brew install masscan
- Ubuntu/Debian: sudo apt-get install masscan
"""
    except Exception as e:
        return f"""
Failed to run masscan: {str(e)}

📋 Command to run locally:
sudo {command_string}
"""


@mcp.tool()
def masscan_help() -> str:
    """
    Get help information about masscan and this MCP server.
    """
    return """
# Masscan MCP Server

## About Masscan
Masscan is a fast port scanner capable of scanning the entire internet in under 6 minutes.
It's designed for speed and can transmit up to 10 million packets per second.

## Platform Limitations
⚠️ This server is running on a containerized cloud platform (Render.com).
Due to security restrictions, raw socket operations (required for port scanning) 
are NOT available. The platform does not grant CAP_NET_RAW capability to containers.

## What This Tool Does
Instead of running scans directly, this tool:
1. Generates the correct masscan command based on your parameters
2. Provides instructions for running the command locally
3. Shows installation instructions for masscan

## Running Masscan Locally
To run masscan on your own machine:

1. Install masscan:
   - macOS: `brew install masscan`
   - Ubuntu/Debian: `sudo apt-get install masscan`
   - Arch Linux: `sudo pacman -S masscan`

2. Run with sudo (required for raw sockets):
   `sudo masscan -p80,443 target.com`

3. Or use Docker with capabilities:
   `docker run --rm --cap-add=NET_RAW masscan/masscan -p80 target.com`

## Example Commands
- Scan common ports: `sudo masscan -p22,80,443 192.168.1.0/24`
- Scan with rate limit: `sudo masscan -p80 10.0.0.0/8 --max-rate 1000`
- Full port scan: `sudo masscan -p0-65535 target.com --max-rate 10000`

## Why This Limitation Exists
Cloud platforms disable raw socket access to:
- Prevent abuse (DDoS attacks, network scanning)
- Maintain security isolation between containers
- Comply with acceptable use policies

For actual scanning capabilities, deploy on:
- A VPS (AWS EC2, DigitalOcean, Linode)
- Your own server with Docker --cap-add=NET_RAW
- Your local machine with sudo access
"""


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
