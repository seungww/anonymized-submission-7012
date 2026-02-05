import argparse
import os
import json

# Loaded from usermap file
USER_MAP = {}

# SSRC to media type mapping based on RTP packets
SSRC_MEDIA = {}


def get_usermap_path_from_hex(hex_path: str) -> str:
    hex_dir = os.path.dirname(os.path.abspath(hex_path))
    parent_dir = os.path.dirname(hex_dir)
    parent_name = os.path.basename(parent_dir)

    if not parent_name:
        parent_name = "default"

    return os.path.join(parent_dir, f"usermap_{parent_name}.json")


def load_usermap(path: str) -> dict:
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def get_user_from_ssrc(ssrc_hex: str):
    """Returns mapped user or None if not found."""
    return USER_MAP.get(ssrc_hex)


def parse_line(tokens, args):
    """Parse one UDP payload (hex tokens)."""
    if len(tokens) < 8:
        return ""

    try:
        b = [int(t, 16) for t in tokens]
    except ValueError:
        return ""

    # RTP common header fields
    b0 = b[0]
    version = (b0 >> 6) & 0x03
    if version != 2:
        return ""

    pt_byte = b[1]
    rtcp_pt = pt_byte               # RTCP PT (200–210)
    rtp_pt = pt_byte & 0x7F         # RTP PT (marker bit removed)

    sender = recipient = subject = typ = value = None

    # ==========================
    # RTP PATH
    # ==========================
    if not (200 <= rtcp_pt <= 210):

        # Need basic RTP header
        if len(b) < 12:
            return ""

        cc = b0 & 0x0F            # CSRC count
        x = (b0 & 0x10) >> 4      # extension flag

        # Compute RTP header length
        rtp_header_len = 12 + cc * 4

        # Parse RTP header extension
        ext_count = 0
        if x and len(b) >= rtp_header_len + 4:
            ext_pos = rtp_header_len
            ext_len_words = (b[ext_pos + 2] << 8) | b[ext_pos + 3]
            ext_total = 4 + ext_len_words * 4
            if ext_pos + ext_total <= len(b):
                rtp_header_len = ext_pos + ext_total
                ext_count = ext_len_words

        # Extract SSRC
        ssrc_bytes = b[8:12]
        if len(ssrc_bytes) != 4:
            return ""
        ssrc_hex = ''.join(f"{x:02X}" for x in ssrc_bytes)

        # Extract CSRC (first only)
        csrc_hex = None
        if cc > 0 and len(b) >= 16:
            csrc_bytes = b[12:16]
            if len(csrc_bytes) == 4:
                csrc_hex = ''.join(f"{x:02X}" for x in csrc_bytes)

        # Determine media type and value
        media = None
        if rtp_pt == 120:
            media = "video"
            typ = "video"

            if ext_count == 1:
                value = "low"
            elif ext_count > 1:
                value = "high"
            else:
                return ""   # skip packet if extension count not allowed

        elif rtp_pt == 109:
            media = "audio"
            typ = "audio"
            value = "unmute"
        else:
            return ""

        # Store media type for RTCP later
        SSRC_MEDIA[ssrc_hex] = media

        # Determine user using CSRC first
        user = None
        if csrc_hex and csrc_hex in USER_MAP:
            user = USER_MAP[csrc_hex]
        elif ssrc_hex in USER_MAP:
            user = USER_MAP[ssrc_hex]
        else:
            return ""   # no mapping → skip

        # Assign sender/recipient/subject
        if user == args.client:
            sender = recipient = subject = user
            if typ == "video":
                value = "on"
        else:
            sender = subject = user
            recipient = args.client

    else:
        # First 8 bytes are cleartext
        if len(b) < 8:
            return ""

        # SSRC in bytes 4–7
        ssrc_bytes = b[4:8]
        if len(ssrc_bytes) != 4:
            return ""
        ssrc_hex = ''.join(f"{x:02X}" for x in ssrc_bytes)

        # Media type must already be known from RTP
        media = SSRC_MEDIA.get(ssrc_hex)
        if not media:
            return ""

        if media == "video":
            typ = "video"
            value = "on"
        elif media == "audio":
            typ = "audio"
            value = "unmute"
        else:
            return ""

        # SSRC must be mapped to a user
        if ssrc_hex not in USER_MAP:
            return ""

        user = USER_MAP[ssrc_hex]

        # sender/recipient/subject assignment
        if user == args.client:
            sender = recipient = subject = user
        else:
            sender = subject = user
            recipient = args.client

    if sender and recipient and subject and typ and value:
        return f"{sender}_{recipient}_{subject}_{typ}_{value}"
    elif sender and recipient and subject and typ:
        return f"{sender}_{recipient}_{subject}_{typ}"

    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hex', type=str, required=True)
    parser.add_argument('--client', type=str, required=True)
    parser.add_argument('--usermap', type=str, required=False,
                        help='Optional path to usermap JSON file')
    args = parser.parse_args()

    # Determine usermap path
    if args.usermap:
        usermap_path = args.usermap
    else:
        usermap_path = get_usermap_path_from_hex(args.hex)

    global USER_MAP
    USER_MAP = load_usermap(usermap_path)

    with open(args.hex, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) < 8:
                print("")
                continue
            print(parse_line(tokens, args))


if __name__ == '__main__':
    main()

