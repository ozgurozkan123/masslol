FROM python:3.11-slim

# Install system dependencies including masscan and sudo
RUN apt-get update && apt-get install -y \
    masscan \
    sudo \
    curl \
    libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

# Give masscan the capability to use raw sockets without full root
# This allows masscan to send raw packets
RUN setcap cap_net_raw+ep /usr/bin/masscan

# Configure sudo to allow masscan without password for any user
RUN echo "ALL ALL=(ALL) NOPASSWD: /usr/bin/masscan" >> /etc/sudoers

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

CMD ["python", "server.py"]
