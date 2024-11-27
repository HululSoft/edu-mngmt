#!/bin/bash

# Check if the /app/data directory exists; create it if it doesn't
if [ ! -d /app/data ]; then
    echo "Creating /app/data directory..."
    mkdir -p /app/data
fi

# Copy missing files from /default-data to /app/data
echo "Syncing missing files from /default-data to /app/data..."
for file in /default-data/*; do
    target="/app/data/$(basename "$file")"
    if [ ! -e "$target" ]; then
        echo "Copying $(basename "$file") to /app/data..."
        cp -r "$file" "$target"
    fi
done

# Run the application
exec "$@"
