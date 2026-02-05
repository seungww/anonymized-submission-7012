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

# Enter twice
xdotool key Return
sleep 1

xdotool key Return
sleep 2

# Tab then Enter to copy link
xdotool key Tab
sleep 0.4

xdotool key Return
sleep 0.6

# Read copied link from clipboard
if ! command -v xclip >/dev/null 2>&1; then
    echo "[FAIL] xclip not installed"
    exit 1
fi

MEET_LINK=$(xclip -o -selection clipboard 2>/dev/null)

if [ -z "$MEET_LINK" ]; then
    echo "[FAIL] Clipboard empty, no link copied"
    exit 1
fi

echo "[INFO] Copied link: $MEET_LINK"

# Paste link into address bar and navigate
xdotool key ctrl+l
sleep 0.3
xdotool type "$MEET_LINK"
sleep 0.3
xdotool key Return
sleep 3

# One more Enter as requested
xdotool key Return
sleep 2

# Extract meeting code
MEET_CODE=$(echo "$MEET_LINK" | sed -E 's#^https?://meet.google.com/([^/?]+).*#\1#')

if [ -z "$MEET_CODE" ]; then
    echo "[FAIL] Could not extract code"
    exit 1
fi

echo "$MEET_CODE"

