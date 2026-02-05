import argparse
import json
import os
import glob
import dpkt

def parse_pcap(pcap_path):
    """Extract timestamps from pcap file (in ms, first packet as 0s)"""
    timestamps = []
    with open(pcap_path, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        base_ts = None
        for ts, _ in pcap:
            if base_ts is None:
                base_ts = ts
            rel_ts = (ts - base_ts) * 1000  # convert to ms
            timestamps.append(rel_ts)
    return timestamps

def parse_ui_files(target_dir):
    """Return dict of frame_time -> parameters from .ui files"""
    ui_data = {}
    for ui_file in glob.glob(os.path.join(target_dir, "*.ui")):
        fname = os.path.basename(ui_file)
        frame_idx = int(fname.split("_")[-1].split(".")[0])  # extract frame index (000001)
        frame_time = frame_idx * 0.1  # seconds (10 fps = 0.1s per frame)
        with open(ui_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            params = []
            for p in data.get("parameters", []):
                if p['value'] not in ['unknown', 'off', 'mute']:
                    params.append(f"{p['sender']}_{p['recipient']}_{p['subject']}_{p['type']}_{p['value']}")
                    # params.append(f"{p['subject']}_{p['type']}_{p['value']}")
                    # params.append(f"{p['subject']}_{p['type']}")
                    # params.append(f"{p['type']}_{p['value']}")
                    # params.append(f"{p['subject']}_{p['value']}")
                    # params.append(f"{p['subject']}")
                    # params.append(f"{p['type']}")
                    # params.append(f"{p['value']}")
        ui_data[frame_time] = params
    return ui_data

def match_timestamps(pcap_ts, ui_data):
    """Match pcap timestamps with ui parameters within ±0.25s"""
    results = []
    for ts in pcap_ts:
        sec = ts / 1000.0  # convert to seconds
        matched = set()
        for frame_time, params in ui_data.items():
            if abs(sec - frame_time) <= 0.25:
                matched.update(params)
        row = list(matched)  # ms timestamp
        results.append(row)
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", required=True, help="Input pcap file")
    parser.add_argument("--target", required=True, help="Directory containing .ui files")
    args = parser.parse_args()

    pcap_ts = parse_pcap(args.pcap)
    ui_data = parse_ui_files(args.target)
    results = match_timestamps(pcap_ts, ui_data)

    # Output as CSV style
    for row in results:
        print(",".join(row))

if __name__ == "__main__":
    main()

