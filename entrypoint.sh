#!/bin/bash

# Check if the /app/data directory is empty
if [ ! "$(ls -A /app/data)" ]; then
    echo "Initializing data directory with default content..."
    cp -r /default-data/* /app/data/
else
    echo "Data directory already initialized."
fi

# Run the application
exec "$@"
