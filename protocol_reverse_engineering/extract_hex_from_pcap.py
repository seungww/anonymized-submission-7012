import argparse
from scapy.all import rdpcap, UDP
import os

def extract_udp_payloads(pcap_file, max_bytes=80):
    packets = rdpcap(pcap_file)
    hex_lines = []

    for pkt in packets:
        if UDP in pkt:
            udp_payload = bytes(pkt[UDP].payload)[:max_bytes]
            hex_str = ' '.join(f"{byte:02X}" for byte in udp_payload)
            hex_lines.append(hex_str)

    return hex_lines

def save_hex_output(hex_lines, output_path):
    with open(output_path, 'w') as f:
        for line in hex_lines:
            f.write(line + '\n')

def main():
    parser = argparse.ArgumentParser(description="Extract UDP payloads in hex format from pcap")
    parser.add_argument("--pcap", required=True, help="Path to the pcap file")
    args = parser.parse_args()

    pcap_path = args.pcap
    hex_lines = extract_udp_payloads(pcap_path)

    hex_path = os.path.splitext(pcap_path)[0] + '.hex'
    save_hex_output(hex_lines, hex_path)

    print(f"Hex output saved to {hex_path}")

if __name__ == "__main__":
    main()

