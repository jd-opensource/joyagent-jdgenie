#!/bin/bash
set -e

# Python script startup script for genie-backend-python
# This is the Python equivalent of the Java start.sh script

# Script directory
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
# Project root directory
BASE_DIR=$(cd "$SCRIPT_DIR/.."; pwd)
cd "$BASE_DIR"

# App name
APP_NAME=${APP_NAME:-"genie-backend-python"}

# Log directory
LOG_DIR="/export/Logs/$APP_NAME"
LOG_FILE="$LOG_DIR/${APP_NAME}_startup.log"

# Python environment
PYTHON_CMD=${PYTHON_CMD:-"python3"}
VENV_PATH=${VENV_PATH:-"$BASE_DIR/venv"}

echo "Current path: $BASE_DIR"

# Create log directory
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    if [ $? -ne 0 ]; then
        echo "Cannot create $LOG_DIR" >&2
        exit 1
    fi
fi

# Function to get process ID
function get_pid() {
    pgrep -f "python.*genie_application.py"
}

# Check if app is already running
if [[ -n $(get_pid) ]]; then
    echo "ERROR: $APP_NAME already running" >&2
    exit 1
fi

echo "Starting $APP_NAME ...."

# Activate virtual environment if it exists
if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment at $VENV_PATH"
    source "$VENV_PATH/bin/activate"
fi

# Check if required packages are installed
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Start the application
export PYTHONPATH="$BASE_DIR/src/main/python:$PYTHONPATH"
nohup $PYTHON_CMD genie_application.py > "$LOG_FILE" 2>&1 &

# Wait for application to start
sleep 10

# Check if application started successfully
if [[ -n $(get_pid) ]]; then
    echo "$APP_NAME is up and running :)"
    echo "Log file: $LOG_FILE"
    echo "Process ID: $(get_pid)"
else
    echo "ERROR: $APP_NAME failed to start" >&2
    echo "Check log file: $LOG_FILE"
    exit 1
fi