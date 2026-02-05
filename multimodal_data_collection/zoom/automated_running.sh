#!/bin/bash

HOSTS=("tmv-red" "tmv-green" "tmv-blue" "tmv-cyan" "tmv-magenta" "tmv-yellow")
PARTICIPANTS=("tmv-green" "tmv-blue" "tmv-cyan" "tmv-magenta")

SCRIPTS_DIR="~/Scripts/zoom"

LOG_DIR="./recordings"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

ALL_LOG="$LOG_DIR/remote_tmv-all_${TIMESTAMP}.log"

run_remote() {
    local host=$1
    local cmd=$2
    local host_log="$LOG_DIR/remote_${host}_${TIMESTAMP}.log"

    {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $host: $cmd started"
        ssh "$host" "cd $SCRIPTS_DIR && $cmd"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $host: $cmd completed"
        echo
    } | tee -a "$host_log" >> "$ALL_LOG"
}

# 1) Start recording on all hosts
for h in "${HOSTS[@]}"; do
    run_remote "$h" "./start_record.sh" &
done
wait


# 2) Create new meeting on tmv-red
run_remote tmv-red "./maximize_zoom.sh"
sleep 1
run_remote tmv-red "./click_new_meeting.sh"
sleep 1
run_remote tmv-red "./change_to_speaker.sh"
sleep 1
run_remote tmv-red "./toggle_audio.sh"
sleep 1
run_remote tmv-red "./toggle_video.sh"
sleep 1

# 3) Join remaining hosts
for h in tmv-green tmv-blue tmv-cyan tmv-magenta; do
    run_remote "$h" "./maximize_zoom.sh"
    sleep 1
    run_remote "$h" "./click_join_meeting.sh"
    sleep 1
    run_remote "$h" "./change_to_speaker.sh"
    sleep 1
    run_remote "$h" "./toggle_audio.sh"
    sleep 1
    run_remote "$h" "./toggle_video.sh"
    sleep 1
done

# 4) Turn on the waiting room
run_remote tmv-red "./toggle_waiting_room.sh"
sleep 5

run_remote tmv-yellow "./maximize_zoom.sh"
sleep 1
run_remote tmv-yellow "./click_join_meeting.sh"
sleep 1

# 5) Execute five random participant-action pairs

actions=(
    "./toggle_audio.sh"
    "./toggle_video.sh"
    "./action_first_pin.sh"
    "./action_second_pin.sh"
    "./action_third_pin.sh"
    "./action_fourth_pin.sh"
)

for i in {1..5}; do
    host=${PARTICIPANTS[$RANDOM % ${#PARTICIPANTS[@]}]}
    action=${actions[$RANDOM % ${#actions[@]}]}
    run_remote "$host" "$action"
    sleep 10
done

# 5) End meeting on tmv-red
run_remote tmv-red "./toggle_end.sh"
sleep 1

# 6) Stop recordings on all hosts
for h in "${HOSTS[@]}"; do
    run_remote "$h" "./stop_record.sh" &
done
wait
