#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Move mouse to specific coordinates in the Zoom window and click
if xdotool search --name "Zoom Workplace - Free account" mousemove --window %1 428 298 click 1; then
    echo "[OK] Mouse moved and click sent to Zoom Workplace"
    echo "[OK] Wait 5 seconds"
    sleep 5
else
    echo "[FAIL] Could not find Zoom Workplace window or send click"
fi
