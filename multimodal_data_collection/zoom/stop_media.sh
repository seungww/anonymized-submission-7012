#!/bin/bash
# stop_media.sh
# Stop audio/video feeders, free devices, unload modules. Minimal [OK]/[FAIL] logs.

set -euo pipefail
ok(){ echo "[OK] $*"; }
fail(){ echo "[FAIL] $*"; }

# 1) stop our feeder processes via PID files
[ -f /tmp/audio_loop.pid ] && kill "$(cat /tmp/audio_loop.pid)" 2>/dev/null || true
[ -f /tmp/video_loop.pid ] && kill "$(cat /tmp/video_loop.pid)" 2>/dev/null || true
sleep 0.4

# 2) fallback: kill by unique patterns to avoid dangling instances
pkill -f 'ffmpeg .* -f alsa .*Loopback,1,' 2>/dev/null || true
pkill -f 'ffmpeg .* -f v4l2 /dev/video0' 2>/dev/null || true
pkill -x aplay arecord 2>/dev/null || true
pkill -x zoom 2>/dev/null || true
sleep 0.3

# 3) force-free device nodes if still busy
sudo fuser -km /dev/snd/* >/dev/null 2>&1 || true
sudo fuser -km /dev/video0 >/dev/null 2>&1 || true
sleep 0.3

# 4) unload modules
if sudo modprobe -r snd_aloop snd_dummy 2>/dev/null; then
  ok "modules unloaded"
else
  fail "modules still in use"
fi

# 5) clean pid files
rm -f /tmp/audio_loop.pid /tmp/video_loop.pid 2>/dev/null || true

