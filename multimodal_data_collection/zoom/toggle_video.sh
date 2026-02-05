#!/bin/bash
# Send Alt+V keystroke to Zoom "Meeting" window (toggle video start/stop)

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+V to that window
    xdotool key --window "$WIN_ID" alt+v
    echo "[OK] Sent Alt+V to Zoom"
else
    echo "[FAIL] Meeting window not found"
fi


