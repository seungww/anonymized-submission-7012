#!/bin/bash
# Bring up a stable virtual mic (ALSA Loopback) and a virtual camera (v4l2loopback), then feed audio/video endlessly.

set -e

# -----------------------------
# Display (for apps that need X)
# -----------------------------
export DISPLAY=:10.0

# -----------------------------
# Load kernel modules (audio)
# - snd-aloop as card0 (pinned via /etc/modprobe.d)
# - snd-dummy as card1 (pinned via /etc/modprobe.d)
# -----------------------------
echo 'options snd-aloop index=0'  | sudo tee /etc/modprobe.d/99-virt-audio.conf
echo 'options snd-dummy index=1'  | sudo tee -a /etc/modprobe.d/99-virt-audio.conf

sudo modprobe snd-aloop
sudo modprobe snd-dummy

# -----------------------------
# Load kernel module (video)
# -----------------------------
sudo depmod -a
sudo modprobe v4l2loopback

# -----------------------------
# Start infinite audio loop
# - Feed to Loopback playback (1,0)
#   (paired capture side is Loopback (0,0))
# -----------------------------
ffmpeg -re -stream_loop -1 -nostdin \
  -i audio32.wav \
  -f alsa plughw:Loopback,1,0 \
  </dev/null >/dev/null 2>&1 &
A_PID=$!

# -----------------------------
# Start infinite video loop
# - Feed to virtual camera /dev/video0
# -----------------------------
ffmpeg -re -stream_loop -1 -nostdin -nostats \
  -i video.mp4 \
  -f v4l2 /dev/video0 \
  </dev/null >/dev/null 2>&1 &
V_PID=$!

sleep 1

# -----------------------------
# Verify audio feeder process
# -----------------------------
if kill -0 "$A_PID" >/dev/null 2>&1; then
  echo "[OK] audio loop running (PID $A_PID)"
else
  echo "[FAIL] audio loop not running"
fi

# -----------------------------
# Quick mic probe (capture 0,0)
# -----------------------------
if arecord -q -D hw:Loopback,0,0 -f cd -d 1 /tmp/virtmic_probe.wav >/dev/null 2>&1; then
  echo "[OK] mic capture works (Loopback,0,0)"
  rm -f /tmp/virtmic_probe.wav
else
  echo "[FAIL] mic capture failed (Loopback,0,0)"
fi

# -----------------------------
# Verify video feeder process
# -----------------------------
if kill -0 "$V_PID" >/dev/null 2>&1; then
  echo "[OK] video loop running (PID $V_PID)"
else
  echo "[FAIL] video loop not running"
fi

# -----------------------------
# Verify virtual camera device
# -----------------------------
if [ -e /dev/video0 ]; then
  echo "[OK] /dev/video0 exists"
else
  echo "[FAIL] /dev/video0 not found"
fi

# -----------------------------
# Smoke test: read one frame from /dev/video0
# -----------------------------
if ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 -f null - >/dev/null 2>&1; then
  echo "[OK] /dev/video0 is producing video"
else
  echo "[FAIL] /dev/video0 cannot be read"
fi

