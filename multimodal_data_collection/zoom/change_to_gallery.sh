#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Maximize the meeting window
wmctrl -r "Meeting" -b add,maximized_vert,maximized_horz

# Check if the "Meeting" window exists
if wmctrl -l | grep -q "Meeting"; then
    echo "[OK] Meeting window found and maximize command sent"
else
    echo "[FAIL] Meeting window not found"
fi
sleep 1

# WIN_ID=$(xdotool search --name "Zoom" | head -n 1)
xdotool mousemove 1281 69
sleep 1
xdotool click 1
sleep 1
xdotool mousemove 1281 144
sleep 1
xdotool click 1
sleep 1
echo "[OK] Change to gallery view"
