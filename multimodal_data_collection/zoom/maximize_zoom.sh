#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

# Maximize the Zoom window
wmctrl -r "Zoom Workplace" -b add,maximized_vert,maximized_horz
sleep 1

# Get screen resolution
screen_width=$(xdpyinfo | awk '/dimensions/{print $2}' | cut -dx -f1)
screen_height=$(xdpyinfo | awk '/dimensions/{print $2}' | cut -dx -f2)

# Get Zoom window position and size
read x y w h <<< $(wmctrl -lG | grep "Zoom Workplace" | awk '{print $3, $4, $5, $6}')

# Compare width only
if [[ "$w" -eq "$screen_width" ]]; then
    echo "[OK] Zoom window width matches screen width"
else
    echo "[FAIL] Zoom window width ${w} != screen width ${screen_width}"
fi

# Display actual measured sizes
echo "[INFO] Zoom window size: ${w}x${h}, Screen size: ${screen_width}x${screen_height}"

