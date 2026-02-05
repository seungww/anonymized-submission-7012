#!/bin/bash

export DISPLAY=:10.0

# Start screen recording + tcpdump (simple version)
# Fixed display :10.0, 1512x944, 30fps, saved to ~/recordings
# Tcpdump capture on eth0, saved to same folder

mkdir -p ~/recordings
TS=$(date +%Y%m%d_%H%M%S)
OUT_VIDEO=~/recordings/record_${TS}.mp4
OUT_PCAP=~/recordings/tcpdump_${TS}.pcap

MYIP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '^127\.')

# Start ffmpeg (screen recording)
nohup ffmpeg -video_size 1512x944 -framerate 10 \
    -f x11grab -i $DISPLAY \
    -c:v libx264 -preset ultrafast -crf 23 \
    "$OUT_VIDEO" >/dev/null 2>&1 &
echo $! > /tmp/screen_recording.pid
echo "[OK] Recording started (PID $!)"

# Start tcpdump (network capture)
nohup tcpdump -i eno1 -U "udp and (src host $MYIP or dst host $MYIP)" -w "$OUT_PCAP" >/dev/null 2>&1 &
echo $! > /tmp/tcpdump.pid
echo "[OK] Tcpdump started (PID $!)"
