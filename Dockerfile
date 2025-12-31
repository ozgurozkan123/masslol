FROM python:3.11-slim

# Install system dependencies including masscan
RUN apt-get update && apt-get install -y \
    masscan \
    curl \
    && rm -rf /var/lib/apt/lists/*

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
