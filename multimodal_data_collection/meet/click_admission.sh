#!/bin/bash

export DISPLAY=:10.0

# Find Firefox window
FIREFOX_WIN=$(xdotool search --onlyvisible --class "Firefox" | head -n 1)

if [ -z "$FIREFOX_WIN" ]; then
    echo "[FAIL] No Firefox window found"
    exit 1
fi

echo "[OK] Found Firefox window: $FIREFOX_WIN"

xdotool mousemove 1333 909
# xdotool mousemove --window "$FIREFOX_WIN" 1333 909
sleep 0.5
xdotool click 1
echo "[OK] Clicked at 1333 909"

sleep 3

# xdotool mousemove --window "$FIREFOX_WIN" 1392 445
xdotool mousemove 1402 494
sleep 0.5
for i in {1..4}; do
    xdotool click 1
    echo "[OK] Clicked at 1392 445 ($i/5)"
    sleep 3
done

xdotool mousemove 1333 909
# xdotool mousemove --window "$FIREFOX_WIN" 1333 909
sleep 0.5
xdotool click 1
echo "[OK] Clicked at 1333 909"
