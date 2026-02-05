#!/bin/bash
# Send Alt+U keystroke to Zoom "Meeting" window (toggle participants panel)

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


