#!/bin/bash

# Set display for remote GUI session
export DISPLAY=:10.0

xdotool mousemove 874 920
sleep 3
xdotool click 1
sleep 1
xdotool mousemove 874 347
sleep 3
xdotool click 1
sleep 1
echo "[OK] Enable waiting room"
