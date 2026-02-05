#!/bin/bash
# Send Alt+S keystroke to Zoom "Meeting" window (toggle screen-sharing start/stop)

# Set display for remote GUI session
export DISPLAY=:10.0

xdotool mousemove 864 156
sleep 1
xdotool click 1
sleep 1
echo "[OK] End screen sharing"
