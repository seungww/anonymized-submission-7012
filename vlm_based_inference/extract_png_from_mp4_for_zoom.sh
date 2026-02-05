#!/bin/bash
# Usage: ./extract_png_from_mp4.sh <video_file> <fps> <max_width> [start_time_sec]

if [ $# -lt 3 ] || [ $# -gt 4 ]; then
    echo "Usage: $0 <video_file> <fps> <max_width> [start_time_sec]"
    echo "Example: $0 record_20250811_152411.mp4 10 1512 200" # 210
    exit 1
fi

VIDEO="$1"
FPS="$2"
MAX_WIDTH="$3"
START_TIME="${4:-0}"  # default 0 if not given
BASENAME=$(basename "$VIDEO" .mp4)
VID_DIR=$(dirname "$VIDEO")
OUTDIR="$VID_DIR/$BASENAME"

mkdir -p "$OUTDIR"

# Extract frames starting from START_TIME
ffmpeg -ss "$START_TIME" -i "$VIDEO" -vf "fps=$FPS,scale=${MAX_WIDTH}:-1" "$OUTDIR/frame_%06d.png"

echo "[OK] Frames extracted from ${START_TIME}s at $FPS fps into '$OUTDIR' with max width $MAX_WIDTH"

