#!/bin/bash
# Stop screen recording + tcpdump (simple version)

# Stop ffmpeg
if [ -f /tmp/screen_recording.pid ]; then
    kill -INT "$(cat /tmp/screen_recording.pid)" 2>/dev/null
    rm -f /tmp/screen_recording.pid
    echo "[OK] Recording stopped"
else
    echo "[FAIL] No recording PID found"
fi

# Stop tcpdump
if [ -f /tmp/tcpdump.pid ]; then
    kill -INT "$(cat /tmp/tcpdump.pid)" 2>/dev/null
    rm -f /tmp/tcpdump.pid
    echo "[OK] tcpdump stopped"
else
    echo "[FAIL] No tcpdump PID found"
fi
