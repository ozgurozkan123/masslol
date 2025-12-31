import os
import subprocess
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("masscan-mcp")


@mcp.tool()
def do_masscan(target: str, port: str, masscan_args: list[str] = None) -> str:
    """
    Generate a masscan command for port scanning. MASSCAN is a fast port scanner.
    The primary input parameters are the IP addresses/ranges you want to scan, and the port numbers.
    
    ⚠️ IMPORTANT: Masscan requires raw socket access (CAP_NET_RAW) which is NOT available
    on cloud container platforms like Render. This tool generates the command for you to
    run on your own machine/server with proper permissions.

    Args:
        target: Target information. Example: 1.1.1.1 or 10.0.0.0/8
        port: Target port. Example: 1234 or 0-65535
        masscan_args: Additional masscan arguments like --max-rate
    """
    # Build command arguments
    cmd_parts = ["masscan", f"-p{port}", target]
    
    if masscan_args:
        cmd_parts.extend(masscan_args)
    
    command_string = " ".join(cmd_parts)
    
    return f"""📋 Masscan Command Generated

🔧 Command to run (requires root/sudo):
sudo {command_string}

🐳 Docker alternative (with raw socket capability):
docker run --rm --cap-add=NET_RAW masscan/masscan -p{port} {target}

💻 Installation instructions:
• macOS: brew install masscan
• Ubuntu/Debian: sudo apt-get install masscan
• Arch Linux: sudo pacman -S masscan
• From source: https://github.com/robertdavidgraham/masscan

⚠️ Platform Note:
This MCP server is running on Render.com, which does NOT allow raw socket access 
(CAP_NET_RAW capability) for security reasons. Masscan requires this capability 
to send SYN packets directly. 

To actually perform scans, run the command above on:
• Your local machine (with sudo)
• A VPS (AWS EC2, DigitalOcean, Linode, etc.)
• Docker with --cap-add=NET_RAW flag
• Any system where you have raw socket permissions"""


@mcp.tool()
def masscan_help() -> str:
    """
    Get help information about masscan and this MCP server.
    """
    return """# Masscan MCP Server Help

## About Masscan
Masscan is the fastest port scanner - capable of scanning the entire internet in under 6 minutes.
It can transmit up to 10 million packets per second.

## ⚠️ Platform Limitations
This server runs on Render.com. Due to security restrictions, raw socket operations 
(required for port scanning) are NOT available. The platform doesn't grant CAP_NET_RAW.

## What This Tool Does
This tool generates correct masscan commands based on your parameters.
Run the generated commands on a system with proper permissions.

## Example Commands
• Scan common ports: `sudo masscan -p22,80,443 192.168.1.0/24`
• Scan with rate limit: `sudo masscan -p80 10.0.0.0/8 --max-rate 1000`
• Full port scan: `sudo masscan -p0-65535 target.com --max-rate 10000`
• Banner grabbing: `sudo masscan -p80 target.com --banners`

## Running Masscan Locally

1. Install masscan:
   - macOS: `brew install masscan`
   - Ubuntu/Debian: `sudo apt-get install masscan`
   - From source: https://github.com/robertdavidgraham/masscan

2. Run with sudo (required for raw sockets):
   `sudo masscan -p80,443 target.com`

3. Or use Docker with capabilities:
   `docker run --rm --cap-add=NET_RAW masscan/masscan -p80 target.com`

## Why Raw Sockets Are Needed
Masscan sends SYN packets directly (bypassing the OS TCP stack) for speed.
This requires CAP_NET_RAW capability, which cloud platforms disable for security."""


# Run the server with SSE transport (provides both /mcp and /mcp/sse endpoints)
if __name__ == "__main__":
    # Get host and port from environment (Render sets PORT automatically)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    
    mcp.run(
        transport="sse",  # SSE provides both HTTP (/mcp) and SSE (/mcp/sse) endpoints
        host=host,
        port=port,
        path="/mcp"
    )
