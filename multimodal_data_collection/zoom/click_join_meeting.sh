#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Move mouse to specific coordinates in the Zoom window and click
if xdotool search --name "Zoom Workplace - Free account" mousemove --window %1 527 300 click 1; then
    echo "[OK] Mouse moved and click sent to Zoom Workplace"
    echo "[OK] Wait 5 seconds"
    sleep 5
else
    echo "[FAIL] Could not find Zoom Workplace window or send click"
fi

if xdotool search --name 'Zoom Workplace' mousemove 617 422 click 1; then
    xdotool type 2917062427
    sleep 1
    xdotool key Return
    echo "[OK] Enter meeting ID"
    echo "[OK] Wait 3 seconds"
    sleep 3
    xdotool type 123123
    sleep 1
    xdotool key Return
    echo "[OK] Enter meeting PW"
    echo "[OK] Wait 10 seconds"
    sleep 10
else
    echo "[FAIL] Could not find Zoom Workplace window or send click"
fi
