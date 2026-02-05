#!/bin/bash
# Send Alt+A keystroke to Zoom "Meeting" window (toggle mute/unmute)

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+A to that window
    xdotool key --window "$WIN_ID" alt+a
    echo "[OK] Sent Alt+A to Zoom"
else
    echo "[FAIL] Meeting window not found"
fi


