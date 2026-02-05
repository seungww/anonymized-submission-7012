#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

MEET_CODE=$1

if [ -z "$MEET_CODE" ]; then
    echo "Usage: $0 <meet-code>"
    exit 1
fi

MEET_URL="https://meet.google.com/${MEET_CODE}"

echo "[INFO] Target Google Meet URL: $MEET_URL"

# Find existing Firefox window
FIREFOX_WIN=$(xdotool search --onlyvisible --class "Firefox" | head -n 1)

if [ -z "$FIREFOX_WIN" ]; then
    echo "[FAIL] No Firefox window found"
    exit 1
fi

echo "[OK] Found Firefox window: $FIREFOX_WIN"

# Activate Firefox window
xdotool windowactivate "$FIREFOX_WIN"
sleep 1

# Focus URL bar and type Meet URL
xdotool key ctrl+l
sleep 0.5
xdotool type "$MEET_URL"
sleep 0.5

# Press Enter to navigate
xdotool key Return
echo "[OK] Enter key sent. Google Meet opening."

sleep 7 
xdotool key Return
# xdotool mousemove --window $FIREFOX_WIN 1139 508 click 1
echo "[OK] Clicked join button"

