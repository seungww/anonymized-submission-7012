#!/bin/bash
# Send Alt+Q keystroke to Zoom "Meeting" window (toggle end meeting)

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+Q to that window
    xdotool key --window "$WIN_ID" alt+q
    echo "[OK] Sent Alt+Q to Zoom"
    sleep 3
    xdotool key --window "$WIN_ID" Return
    echo "[OK] Sent Enter to Zoom"
else
    echo "[FAIL] Meeting window not found"
fi


