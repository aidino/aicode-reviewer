FROM python:3.12-slim

WORKDIR /app

# Install only essential system dependencies without C++ compiler
# to avoid the problematic cpp-12 package
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        postgresql-client \
        redis-tools \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Many packages now provide pre-compiled wheels, so we might not need build tools
RUN pip install --no-cache-dir --only-binary=all -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p neo4j/data neo4j/logs neo4j/import neo4j/plugins

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.webapp.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 