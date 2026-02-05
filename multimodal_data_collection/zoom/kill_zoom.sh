#!/bin/bash

# Attempt to gracefully close Zoom using pkill
pkill -f zoom

# Wait a moment and ensure all Zoom-related processes are terminated
sleep 1
ZOOM_PROCESSES=$(pgrep -f zoom)

if [ -n "$ZOOM_PROCESSES" ]; then
    echo "Force killing remaining Zoom processes..."
    pkill -9 -f zoom
else
    echo "Zoom has been closed successfully."
fi

