#!/bin/bash

# Script to run the Python version of genie-backend with Docker Compose

echo "Starting Genie with Python Backend..."
echo "======================================"

# Check if .env file exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running."
    echo "Especially set your LLM_DEFAULT_BASE_URL, LLM_DEFAULT_APIKEY, and OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Build and start services
echo "Building Docker images..."
docker-compose -f docker-compose-python.yml build

echo "Starting services..."
docker-compose -f docker-compose-python.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "Service Status:"
echo "==============="
docker-compose -f docker-compose-python.yml ps

echo ""
echo "Services are starting up. You can access:"
echo "- UI (Svelte): http://localhost:3000"
echo "- Backend (Python): http://localhost:8080"
echo "- Tool Service: http://localhost:1601"
echo "- MCP Client: http://localhost:8188"
echo ""
echo "To view logs: docker-compose -f docker-compose-python.yml logs -f"
echo "To stop: docker-compose -f docker-compose-python.yml down"