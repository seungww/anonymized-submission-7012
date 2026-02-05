#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Launch Zoom in the background
/usr/bin/zoom &
sleep 30

if pgrep -x zoom > /dev/null; then
    echo "[OK] Zoom process is running"
else
    echo "[FAIL] Zoom process not found"
fi
