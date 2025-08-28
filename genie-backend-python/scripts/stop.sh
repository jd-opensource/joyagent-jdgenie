#!/bin/bash

# Python script stop script for genie-backend-python
# This is the Python equivalent of the Java stop.sh script

# Script directory
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
# Project root directory
BASE_DIR=$(cd "$SCRIPT_DIR/.."; pwd)
cd "$BASE_DIR"

# App name
APP_NAME=${APP_NAME:-"genie-backend-python"}

# Function to get process ID
function get_pid() {
    pgrep -f "python.*genie_application.py"
}

echo "Stopping $APP_NAME ...."

if ! get_pid > /dev/null; then
    echo "App not running, exit"
else
    echo "Found running process: $(get_pid)"
    pkill -TERM -f "python.*genie_application.py"
    
    # Wait up to 30 seconds for graceful shutdown
    for i in {1..30}; do
        if ! get_pid > /dev/null; then
            echo "$APP_NAME stopped gracefully"
            exit 0
        fi
        sleep 1
    done
    
    # Force kill if graceful shutdown failed
    echo "Graceful shutdown timeout, force killing..."
    pkill -9 -f "python.*genie_application.py"
    sleep 5
fi

if get_pid > /dev/null; then
    echo "Stop $APP_NAME failed..."
    exit 1
else
    echo "$APP_NAME stopped successfully"
fi