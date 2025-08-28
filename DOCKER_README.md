# Docker Setup for Genie AI Agent

This project now supports running both Java and Python backend versions using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB of available RAM
- Ports 3000, 8080, 1601, and 8188 available

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and edit it with your configuration:

```bash
cp .env.example .env
```

Edit `.env` and set your API keys:
- `LLM_DEFAULT_BASE_URL` - Your LLM server URL
- `LLM_DEFAULT_APIKEY` - Your LLM API key
- `OPENAI_API_KEY` - OpenAI API key for genie-tool

### 2. Choose Your Backend Version

#### Option A: Run with Java Backend (Original)

```bash
./run-java-version.sh
```

Or manually:

```bash
docker-compose -f docker-compose.yml up -d
```

#### Option B: Run with Python Backend (New)

```bash
./run-python-version.sh
```

Or manually:

```bash
docker-compose -f docker-compose-python.yml up -d
```

## Architecture

### Java Version Stack
- **Frontend**: React UI on port 3000
- **Backend**: Spring Boot Java application on port 8080
- **Tool Service**: Python genie-tool on port 1601
- **MCP Client**: Python genie-client on port 8188

### Python Version Stack
- **Frontend**: Svelte UI on port 3000
- **Backend**: FastAPI Python application on port 8080
- **Tool Service**: Python genie-tool on port 1601
- **MCP Client**: Python genie-client on port 8188

## Service URLs

After starting, services will be available at:
- UI: http://localhost:3000
- Backend API: http://localhost:8080
- Tool Service: http://localhost:1601
- MCP Client: http://localhost:8188

## Docker Compose Commands

### View Logs

Java version:
```bash
docker-compose -f docker-compose.yml logs -f
```

Python version:
```bash
docker-compose -f docker-compose-python.yml logs -f
```

### Stop Services

Java version:
```bash
docker-compose -f docker-compose.yml down
```

Python version:
```bash
docker-compose -f docker-compose-python.yml down
```

### Rebuild Services

Java version:
```bash
docker-compose -f docker-compose.yml build --no-cache
docker-compose -f docker-compose.yml up -d
```

Python version:
```bash
docker-compose -f docker-compose-python.yml build --no-cache
docker-compose -f docker-compose-python.yml up -d
```

## Volumes

Both versions use Docker volumes for persistent data:

### Java Version
- `genie-logs`: Application logs
- `genie-tool-data`: Tool service database

### Python Version
- `genie-python-logs`: Application logs
- `genie-tool-data-python`: Tool service database

## Health Checks

All services include health checks. You can verify service health:

```bash
# Java version
docker-compose -f docker-compose.yml ps

# Python version
docker-compose -f docker-compose-python.yml ps
```

## Troubleshooting

### Port Conflicts

If you encounter port conflicts, you can change the ports in the docker-compose files or set them in your `.env` file.

### Service Not Starting

1. Check logs for the specific service:
```bash
docker-compose -f docker-compose.yml logs [service-name]
```

2. Ensure all required environment variables are set in `.env`

3. Verify Docker has enough resources allocated

### Database Issues

If genie-tool has database issues, remove the volume and restart:

```bash
# Java version
docker volume rm genie-tool-data
docker-compose -f docker-compose.yml up -d genie-tool

# Python version
docker volume rm genie-tool-data-python
docker-compose -f docker-compose-python.yml up -d genie-tool
```

## Development Mode

For development with hot-reload:

### Java Backend Development
```bash
# Mount source code and use development profile
docker-compose -f docker-compose.yml up -d
# Then run your Java IDE with remote debugging
```

### Python Backend Development
```bash
# The Python service automatically reloads on code changes
docker-compose -f docker-compose-python.yml up -d
```

## Performance Comparison

| Aspect | Java Version | Python Version |
|--------|-------------|----------------|
| Startup Time | ~30-60s | ~10-20s |
| Memory Usage | ~512MB-1GB | ~256MB-512MB |
| Request Handling | Synchronous | Async (FastAPI) |
| Concurrency | Thread-based | Coroutine-based |

## Notes

- The Python backend is a direct port of the Java version with identical API endpoints
- Both versions share the same tool service and MCP client
- Configuration files are compatible between versions
- The Svelte UI is used with the Python backend for better integration

## Support

For issues or questions:
1. Check the logs first: `docker-compose logs [service-name]`
2. Verify environment variables are correctly set
3. Ensure Docker has sufficient resources allocated
4. Review the health check endpoints