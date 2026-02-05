import argparse
from scapy.all import PcapReader, PcapWriter
import os

def trim_pcap(input_path, pktcount):
    base = os.path.splitext(input_path)[0]
    output_path = f"{base}_{pktcount}.pcap"

    reader = PcapReader(input_path)
    writer = PcapWriter(output_path, sync=True)

    for i, pkt in enumerate(reader):
        if i >= pktcount:
            break
        writer.write(pkt)

    reader.close()
    writer.close()
    return output_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", required=True, help="path to input pcap")
    parser.add_argument("--pktcount", type=int, required=True, help="number of packets to keep")
    args = parser.parse_args()

    out = trim_pcap(args.pcap, args.pktcount)
    print(f"Saved to {out}")

if __name__ == "__main__":
    main()
