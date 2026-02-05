import argparse
from scapy.all import rdpcap, wrpcap, UDP
import os
import re
import json
from datetime import datetime, timezone


def extract_timestamp_from_filename(filename):
    pattern = r"(\d{8})_(\d{6})"
    match = re.search(pattern, filename)
    if not match:
        raise ValueError("Filename does not contain a valid timestamp pattern")

    date_part = match.group(1)
    time_part = match.group(2)

    dt_str = date_part + time_part
    dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
    return dt.replace(tzinfo=timezone.utc)


def get_usermap_path(pcap_path):
    pcap_dir = os.path.dirname(os.path.abspath(pcap_path))
    parent_dir = os.path.dirname(pcap_dir)
    parent_name = os.path.basename(parent_dir)

    if not parent_name:
        parent_name = "default"

    filename = f"usermap_{parent_name}.json"
    return os.path.join(parent_dir, filename)


def load_usermap(usermap_path):
    if os.path.exists(usermap_path):
        try:
            with open(usermap_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def save_usermap(usermap_path, usermap):
    os.makedirs(os.path.dirname(usermap_path), exist_ok=True)
    with open(usermap_path, "w", encoding="utf-8") as f:
        json.dump(usermap, f, indent=2, sort_keys=False)


def extract_ssrc_from_udp_payload(payload: bytes):
    if len(payload) < 45:
        return None

    if payload[0] != 0x05:
        return None

    mode = payload[7]
    if mode not in (0x00, 0x01):
        return None

    p8 = payload[8]

    if p8 == 0x0F:
        base_offset = 35
    elif p8 == 0x10:
        base_offset = 40
    elif p8 in (0x21, 0x22):
        base_offset = 28
    else:
        return None

    if mode == 0x01:
        base_offset += 7

    if len(payload) < base_offset + 4:
        return None

    ssrc_bytes = payload[base_offset:base_offset + 4]
    return ssrc_bytes.hex().upper()


def filter_pcap(input_pcap, skip_seconds, client_name):
    packets = rdpcap(input_pcap)
    if not packets:
        print("No packets found in the input file.")
        return

    filename = os.path.basename(input_pcap)
    file_start_time = extract_timestamp_from_filename(filename)

    all_filtered = []
    recv_filtered = []
    send_filtered = []

    client_ssrcs = set()

    for pkt in packets:
        pkt_dt = datetime.fromtimestamp(pkt.time, tz=timezone.utc)

        if (pkt_dt - file_start_time).total_seconds() <= skip_seconds:
            continue

        if pkt.haslayer(UDP):
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport

            if sport == 8801 or dport == 8801:
                all_filtered.append(pkt)

                if sport == 8801:
                    recv_filtered.append(pkt)
                if dport == 8801:
                    send_filtered.append(pkt)
                    payload = bytes(pkt[UDP].payload)
                    ssrc_hex = extract_ssrc_from_udp_payload(payload)
                    if ssrc_hex:
                        client_ssrcs.add(ssrc_hex)

    base_name = os.path.basename(input_pcap)
    base_path = os.path.dirname(input_pcap)
    output_all = os.path.join(base_path, f"preprocessed_{base_name}")
    output_recv = os.path.join(base_path, f"recv_{base_name}")
    output_send = os.path.join(base_path, f"send_{base_name}")

    wrpcap(output_all, all_filtered)

    print(f"Saved {len(all_filtered)} filtered packets to: {output_all}")

    # Update usermap
    if client_name and client_ssrcs:
        usermap_path = get_usermap_path(input_pcap)
        usermap = load_usermap(usermap_path)

        new_count = 0
        for ssrc_hex in client_ssrcs:
            if ssrc_hex not in usermap:
                usermap[ssrc_hex] = client_name
                new_count += 1

        if new_count > 0:
            save_usermap(usermap_path, usermap)
            print(f"Added {new_count} new SSRC entries for client '{client_name}' to {usermap_path}")
        else:
            print(f"No new SSRC entries to add for client '{client_name}'")
    else:
        print("No SSRC discovered or client name missing, usermap unchanged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter PCAP and generate usermap from SSRC")
    parser.add_argument("--pcap", required=True, help="Path to the input PCAP file")
    parser.add_argument("--skip", type=int, default=200, help="Seconds to skip after file start time")
    parser.add_argument("--client", required=True, help="Client name to associate with SSRCs")
    args = parser.parse_args()

    filter_pcap(args.pcap, args.skip, args.client)

