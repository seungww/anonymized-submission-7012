#!/bin/bash
# Send Alt+I keystroke to Zoom "Meeting" window (toggle invite window)

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+I to that window
    xdotool key --window "$WIN_ID" alt+i
    echo "[OK] Sent Alt+I to Zoom"
else
    echo "[FAIL] Meeting window not found"
fi


