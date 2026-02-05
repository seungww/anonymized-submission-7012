#!/bin/bash

export DISPLAY=:10.0

BASE_URL="https://meet.google.com"

echo "[INFO] Navigating to $BASE_URL"

# Find Firefox window
FIREFOX_WIN=$(xdotool search --onlyvisible --class "Firefox" | head -n 1)

if [ -z "$FIREFOX_WIN" ]; then
    echo "[FAIL] No Firefox window found"
    exit 1
fi

echo "[OK] Found Firefox window: $FIREFOX_WIN"

xdotool windowactivate "$FIREFOX_WIN"
sleep 1

# Go to meet.google.com
xdotool key ctrl+l
sleep 0.3
xdotool type "$BASE_URL"
sleep 0.2
xdotool key Return
sleep 5

