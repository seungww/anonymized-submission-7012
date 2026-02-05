#!/bin/bash
# Send Alt+S keystroke to Zoom "Meeting" window (toggle screen-sharing start/stop)

# Set display for remote GUI session
export DISPLAY=:10.0

# Find the first window with title containing "Meeting"
WIN_ID=$(xdotool search --name "Meeting" | head -n 1)

if [ -n "$WIN_ID" ]; then
    # Send Alt+S to that window
    xdotool key --window "$WIN_ID" alt+s
    echo "[OK] Sent Alt+S to Zoom"
    sleep 3
else
    echo "[FAIL] Meeting window not found"
fi

WIN_ID=$(xdotool getactivewindow | head -n 1)
xdotool key --window "$WIN_ID" Tab
sleep 1
xdotool keydown Shift
sleep 0.5
xdotool key --window "$WIN_ID" Tab
sleep 0.5
xdotool keyup Shift
sleep 1
xdotool key --window $WIN_ID Return
sleep 1
xdotool key --window "$WIN_ID" Tab
sleep 1
xdotool key --window $WIN_ID Return
sleep 1
