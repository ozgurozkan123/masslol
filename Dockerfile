FROM python:3.11-slim

# Install system dependencies including masscan
RUN apt-get update && apt-get install -y \
    masscan \
    curl \
    libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

# Give masscan the capability to use raw sockets
RUN setcap cap_net_raw,cap_net_admin+eip /usr/bin/masscan

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

# Run as root to allow raw socket access
USER root

CMD ["python", "server.py"]
