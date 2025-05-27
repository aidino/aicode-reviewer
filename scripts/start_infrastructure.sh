#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p neo4j/data neo4j/logs neo4j/import neo4j/plugins

# Function to check if all services are healthy
check_services() {
    local max_attempts=30
    local attempt=1
    local wait_time=10

    echo "Checking services health..."
    while [ $attempt -le $max_attempts ]; do
        # Get service status
        local unhealthy_services=$(docker-compose ps | grep -v "healthy" | grep -v "NAME" | wc -l)
        
        if [ $unhealthy_services -eq 0 ]; then
            echo "✅ All services are healthy!"
            return 0
        fi
        
        echo "Waiting for services to be healthy (attempt $attempt/$max_attempts)..."
        echo "Current status:"
        docker-compose ps
        sleep $wait_time
        attempt=$((attempt + 1))
    done

    echo "❌ Some services are not healthy after $max_attempts attempts"
    echo "Please check the logs with: docker-compose logs"
    return 1
}

# Start all services
echo "Starting services..."
docker-compose down
docker-compose up -d --build

echo "Waiting for services to initialize..."
sleep 20

# Check services health
check_services

if [ $? -eq 0 ]; then
    echo "Infrastructure setup complete!"
    echo "You can access the services at:"
    echo "- Frontend: http://localhost:5173"
    echo "- Backend API: http://localhost:8000"
    echo "- Neo4j Browser: http://localhost:7474"
    echo "- PostgreSQL: localhost:5432"
    echo "- Redis: localhost:6379"
else
    echo "Infrastructure setup failed!"
    exit 1
fi 