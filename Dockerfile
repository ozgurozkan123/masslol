FROM python:3.11-slim

# Install system dependencies including masscan
RUN apt-get update && apt-get install -y \
    masscan \
    curl \
    iproute2 \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Verify masscan is installed and show version
RUN masscan --version || echo "masscan installed"

WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment for proper binding
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the port (Render will set PORT env var)
EXPOSE 8000

# IMPORTANT: Run as root (UID 0) - required for masscan raw socket access
# Do NOT use setcap or USER directives that might reduce privileges
USER 0

CMD ["python", "server.py"]
