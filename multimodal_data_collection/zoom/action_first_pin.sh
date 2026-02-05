#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+U to that window
    xdotool key --window "$WIN_ID" alt+u
    echo "[OK] Sent Alt+U to Zoom"
else
    echo "[FAIL] Meeting window not found"
fi
sleep 3

xdotool mousemove --window "$WIN_ID" 1460 220 # +40
sleep 3
xdotool click 1
sleep 3
xdotool mousemove --window "$WIN_ID" 1460 230
sleep 3
xdotool click 1
sleep 3
xdotool key --window "$WIN_ID" alt+u
echo "[OK] Action Pinning"
