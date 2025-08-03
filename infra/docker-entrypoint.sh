#!/bin/sh
set -e

# Function to wait for backend service
wait_for_backend() {
    echo "Waiting for backend service..."
    while ! nc -z backend 8000; do
        sleep 1
    done
    echo "Backend service started"
}

# Wait for backend if in docker-compose environment
if [ -n "$WAIT_FOR_BACKEND" ]; then
    wait_for_backend
fi

# Execute the main command
exec "$@"