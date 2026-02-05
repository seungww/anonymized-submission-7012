#!/bin/bash
# Set display for remote GUI session
export DISPLAY=:10.0

# Find Firefox window
FIREFOX_WIN=$(xdotool search --onlyvisible --class "Firefox" | head -n 1)

if [ -z "$FIREFOX_WIN" ]; then
    echo "[FAIL] No Firefox window found"
    exit 1
fi

echo "[OK] Found Firefox window: $FIREFOX_WIN"

xdotool windowactivate "$FIREFOX_WIN"
sleep 1


xdotool key --window "$FIREFOX_WIN" ctrl+d
echo "[OK] Sent Ctrl+D to Meet"


