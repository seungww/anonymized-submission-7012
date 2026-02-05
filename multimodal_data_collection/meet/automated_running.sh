#!/bin/bash

HOSTS=("tmv-red" "tmv-green" "tmv-blue" "tmv-cyan" "tmv-magenta" "tmv-yellow")
PARTICIPANTS=("tmv-green" "tmv-blue" "tmv-cyan" "tmv-magenta")
SCRIPTS_DIR="~/Scripts/meet"

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

# 2) Create new meeting on tmv-red and get meeting code
RED_LOG="$LOG_DIR/remote_tmv-red_${TIMESTAMP}.log"

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] tmv-red: ./click_new_meeting.sh started"
} | tee -a "$RED_LOG" >> "$ALL_LOG"

RAW_OUTPUT=$(ssh "tmv-red" "cd $SCRIPTS_DIR && ./click_new_meeting.sh")

printf '%s\n' "$RAW_OUTPUT" | tee -a "$RED_LOG" >> "$ALL_LOG"

MEET_CODE=$(printf '%s\n' "$RAW_OUTPUT" | tail -n 1 | tr -d '\r')

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] tmv-red: ./click_new_meeting.sh completed with code: $MEET_CODE"
    echo
} | tee -a "$RED_LOG" >> "$ALL_LOG"

if [ -z "$MEET_CODE" ]; then
    echo "[ERROR] Meeting code is empty. Aborting."
    exit 1
fi

echo "[INFO] Meeting code: $MEET_CODE"


# 3) Join remaining hosts
for h in tmv-green tmv-blue tmv-cyan tmv-magenta tmv-yellow; do
    run_remote "$h" "./click_join_meeting.sh $MEET_CODE"
    sleep 3
done

# 4) Admission on tmv-red
run_remote tmv-red "./click_admission.sh"
sleep 5

# 5) Execute five random participant-action pairs
actions=(
    "./toggle_audio.sh"
    "./toggle_video.sh"
    "./action_first_pin.sh"
    "./action_second_pin.sh"
    "./action_third_pin.sh"
    "./action_fourth_pin.sh"
)

STATE_DIR="${STATE_DIR:-/tmp/pin_state}"
mkdir -p "$STATE_DIR"

is_pin_action() {
    local a="$1"
    [[ "$a" == ./action_*_pin.sh ]]
}

get_last_action() {
    local host="$1"
    local f="$STATE_DIR/${host}.last"
    [[ -f "$f" ]] && cat "$f"
}

set_last_action() {
    local host="$1"
    local action="$2"
    printf "%s" "$action" > "$STATE_DIR/${host}.last"
}

for i in {1..5}; do
    host=${PARTICIPANTS[$RANDOM % ${#PARTICIPANTS[@]}]}
    rand_action=${actions[$RANDOM % ${#actions[@]}]}
    
    last="$(get_last_action "$host")"
    
    if [[ -n "$last" ]] && is_pin_action "$last"; then
	action_to_run="./action_unpin.sh"
    else
  	action_to_run="$rand_action"
    fi
    
    run_remote "$host" "$action_to_run"
    set_last_action "$host" "$action_to_run"
    
    sleep 10
done

# 6) Stop recordings on all hosts
for h in "${HOSTS[@]}"; do
    run_remote "$h" "./stop_record.sh" &
done
wait

# 7) End meeting (toggle_end) on all hosts
for h in "${HOSTS[@]}"; do
    run_remote "$h" "./toggle_end.sh" &
done
wait

