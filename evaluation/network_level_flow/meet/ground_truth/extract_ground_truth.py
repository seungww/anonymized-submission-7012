#!/usr/bin/env python3
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse SRTP, SRTCP, STUN, and DTLS packets from hex dump lines."
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to input file containing one UDP payload (hex) per line.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Optional number of lines to parse.",
    )
    return parser.parse_args()


def hex_line_to_bytes(line: str) -> list[int]:
    """
    Convert a line containing hex bytes into a list of integers.
    Spaces are optional.
    """
    cleaned = line.strip()
    if not cleaned:
        return []

    no_space = cleaned.replace(" ", "")
    if len(no_space) % 2 != 0:
        raise ValueError(f"Odd number of hex digits in line: {cleaned!r}")

    bytes_list = []
    for i in range(0, len(no_space), 2):
        chunk = no_space[i : i + 2]
        try:
            val = int(chunk, 16)
        except ValueError as exc:
            raise ValueError(f"Invalid hex byte {chunk!r} in line: {cleaned!r}") from exc
        bytes_list.append(val)

    return bytes_list


def is_rtcp_packet(second_byte: int) -> bool:
    """
    Decide if this looks like RTCP based on the second byte.
    For RTCP, the second byte is the RTCP packet type:
    commonly 192–223 (inclusive) according to RFCs.
    """
    return 192 <= second_byte <= 223


def is_stun_packet(payload: list[int]) -> bool:
    """
    Decide if this looks like a STUN message.

    STUN message format:
    - Bytes 0-1: message type (top two bits must be 0)
    - Bytes 2-3: message length (body length in bytes)
    - Bytes 4-7: magic cookie 0x2112A442
    """
    if len(payload) < 20:
        return False

    # Check magic cookie
    if payload[4:8] != [0x21, 0x12, 0xA4, 0x42]:
        return False

    # Top two bits of first byte must be zero
    if payload[0] & 0xC0 != 0:
        return False

    return True


def is_dtls_packet(payload: list[int]) -> bool:
    """
    Decide if this looks like a DTLS record.

    DTLS record header:
    - Byte 0: content type (20, 21, 22, 23)
    - Byte 1: version major (0xFE)
    - Byte 2: version minor (varies, usually 0xFF, 0xFD)
    - Bytes 3-4: epoch
    - Bytes 5-10: sequence number
    - Bytes 11-12: length

    We do NOT require the full record to fit in the datagram,
    so truncated records are still treated as DTLS.
    """
    if len(payload) < 13:
        return False

    content_type = payload[0]
    if content_type not in (20, 21, 22, 23):  # 0x14..0x17
        return False

    version_major = payload[1]
    if version_major != 0xFE:
        return False

    # Optional: basic sanity on length (must be positive)
    length = (payload[11] << 8) | payload[12]
    if length <= 0:
        return False

    # Do not check 13 + length <= len(payload) here,
    # to allow truncated DTLS records.
    return True


def format_byte(b: int) -> str:
    return f"{b:02X}"


def format_block(byte_list: list[int]) -> str:
    """Return bytes as a continuous upper case hex string."""
    return "".join(format_byte(b) for b in byte_list)


def parse_srtp_packet(payload: list[int]) -> str:
    """
    Parse an SRTP packet (RTP header plus encrypted payload).
    Returns a string with logical boundaries separated by spaces.
    """
    if len(payload) < 12:
        return format_block(payload)

    vpxcc = payload[0]
    mpt = payload[1]

    seq_bytes = payload[2:4]
    ts_bytes = payload[4:8]
    ssrc_bytes = payload[8:12]

    cc = vpxcc & 0x0F
    x_bit = (vpxcc & 0x10) >> 4

    offset = 12
    segments: list[str] = []

    # RTP fixed header
    segments.append(format_byte(vpxcc))
    segments.append(format_byte(mpt))
    segments.append(format_block(seq_bytes))
    segments.append(format_block(ts_bytes))
    segments.append(format_block(ssrc_bytes))

    # CSRC list
    csrc_list = []
    if len(payload) < offset + 4 * cc:
        remaining = payload[offset:]
        if remaining:
            segments.append(format_block(remaining))
        return " ".join(segments)

    for _ in range(cc):
        csrc = payload[offset : offset + 4]
        csrc_list.append(csrc)
        offset += 4

    for csrc in csrc_list:
        segments.append(format_block(csrc))

    # Header extension
    if x_bit == 1:
        if len(payload) < offset + 4:
            encrypted_part = payload[offset:]
            if encrypted_part:
                segments.append(format_block(encrypted_part))
            return " ".join(segments)

        ext_profile_bytes = payload[offset : offset + 2]
        ext_profile = (ext_profile_bytes[0] << 8) | ext_profile_bytes[1]
        offset += 2

        ext_length_bytes = payload[offset : offset + 2]
        ext_length = (ext_length_bytes[0] << 8) | ext_length_bytes[1]
        offset += 2

        segments.append(format_block(ext_profile_bytes))
        segments.append(format_block(ext_length_bytes))

        ext_total_bytes = ext_length * 4
        if len(payload) < offset + ext_total_bytes:
            ext_data_bytes = payload[offset:]
            if ext_data_bytes:
                segments.append(format_block(ext_data_bytes))
            return " ".join(segments)

        ext_data_bytes = payload[offset : offset + ext_total_bytes]
        offset += ext_total_bytes

        # RFC 5285 one byte header extensions
        if ext_profile == 0xBEDE:
            pos = 0
            while pos < len(ext_data_bytes):
                b = ext_data_bytes[pos]
                if b == 0x00:
                    pad_start = pos
                    while pos < len(ext_data_bytes) and ext_data_bytes[pos] == 0x00:
                        pos += 1
                    pad_bytes = ext_data_bytes[pad_start:pos]
                    segments.append(format_block(pad_bytes)) 
                    continue

                ext_id = (b & 0xF0) >> 4
                ext_len = (b & 0x0F) + 1
                header_hex = format_byte(b)

                value_start = pos + 1
                value_end = value_start + ext_len
                if value_end > len(ext_data_bytes):
                    rest = ext_data_bytes[pos:]
                    segments.append(format_block(rest))
                    break

                value_bytes = ext_data_bytes[value_start:value_end]
                value_hex = format_block(value_bytes)

                segments.append(header_hex)
                segments.append(value_hex)

                pos = value_end
        else:
            if ext_data_bytes:
                segments.append(format_block(ext_data_bytes))

    encrypted_part = payload[offset:]
    if encrypted_part:
        segments.append(format_block(encrypted_part))

    return " ".join(segments)


def parse_srtcp_packet(payload: list[int]) -> str:
    """
    Parse an SRTCP packet (RTCP header plus encrypted part).
    Returns a string with logical boundaries separated by spaces.

    Format:
    - 1st byte: V P RC
    - 2nd byte: RTCP packet type
    - 3rd and 4th bytes: length (in 32 bit words minus one)
    - Next 4 bytes: SSRC
    - Remaining bytes: encrypted RTCP payload, SRTCP index, auth tag
    """
    if len(payload) < 8:
        return format_block(payload)

    vprc = payload[0]
    pt = payload[1]
    length_bytes = payload[2:4]
    ssrc_bytes = payload[4:8]
    encrypted_part = payload[8:]

    segments = [
        format_byte(vprc),
        format_byte(pt),
        format_block(length_bytes),
        format_block(ssrc_bytes),
    ]
    if encrypted_part:
        segments.append(format_block(encrypted_part))

    return " ".join(segments)


def parse_stun_message(payload: list[int]) -> str:
    """
    Parse a STUN message and return boundaries.

    Format:
    - Bytes 0-1: message type
    - Bytes 2-3: message length (number of bytes in attributes)
    - Bytes 4-7: magic cookie
    - Bytes 8-19: transaction ID
    - Bytes 20-...: attributes

    Attribute format:
    - 2 bytes: type
    - 2 bytes: length
    - N bytes: value
    - padding up to multiple of 4 bytes
    """
    if len(payload) < 20:
        return format_block(payload)

    msg_type_bytes = payload[0:2]
    msg_length_bytes = payload[2:4]
    cookie_bytes = payload[4:8]
    tid_bytes = payload[8:20]

    msg_length = (msg_length_bytes[0] << 8) | msg_length_bytes[1]

    segments: list[str] = []
    segments.append(format_block(msg_type_bytes))
    segments.append(format_block(msg_length_bytes))
    segments.append(format_block(cookie_bytes))
    segments.append(format_block(tid_bytes))

    offset = 20
    attr_region_end = min(len(payload), 20 + msg_length)

    while offset + 4 <= attr_region_end:
        attr_type_bytes = payload[offset : offset + 2]
        attr_length_bytes = payload[offset + 2 : offset + 4]
        attr_length = (attr_length_bytes[0] << 8) | attr_length_bytes[1]

        value_start = offset + 4
        value_end = value_start + attr_length
        if value_end > attr_region_end:
            # Malformed length, dump the rest and stop
            rest = payload[offset:attr_region_end]
            if rest:
                segments.append(format_block(rest))
            offset = attr_region_end
            break

        value_bytes = payload[value_start:value_end]

        segments.append(format_block(attr_type_bytes))
        segments.append(format_block(attr_length_bytes))
        if value_bytes:
            segments.append(format_block(value_bytes))

        # Move to next attribute, including padding to 4 byte boundary
        padded_length = (attr_length + 3) // 4 * 4
        if padded_length > attr_length:
            pad_start = value_end
            pad_end = value_start + padded_length
            pad_bytes = payload[pad_start:pad_end]
            if pad_bytes:
                segments.append(format_block(pad_bytes))
        offset = value_start + padded_length

    # If there are remaining bytes after the declared attribute region
    if offset < len(payload):
        remaining_bytes = payload[offset:]
        if remaining_bytes:
            segments.append(format_block(remaining_bytes))

    return " ".join(segments)


def parse_dtls_records(payload: list[int]) -> str:
    """
    Parse DTLS records from a UDP datagram.

    Each DTLS record:
    - Byte 0: ContentType
    - Bytes 1-2: Version
    - Bytes 3-4: Epoch
    - Bytes 5-10: Sequence number
    - Bytes 11-12: Length
    - Bytes 13-...: Fragment (Length bytes)

    Multiple records may appear consecutively in one datagram.
    Truncated records are still parsed: header fields are output
    and the remaining bytes are treated as fragment.
    """
    segments: list[str] = []
    offset = 0
    total_len = len(payload)

    while offset + 13 <= total_len:
        content_type = payload[offset]
        version_bytes = payload[offset + 1 : offset + 3]
        epoch_bytes = payload[offset + 3 : offset + 5]
        seq_bytes = payload[offset + 5 : offset + 11]
        length_bytes = payload[offset + 11 : offset + 13]

        length = (length_bytes[0] << 8) | length_bytes[1]
        fragment_start = offset + 13
        fragment_end = fragment_start + length

        # Always output header fields
        segments.append(format_byte(content_type))
        segments.append(format_block(version_bytes))
        segments.append(format_block(epoch_bytes))
        segments.append(format_block(seq_bytes))
        segments.append(format_block(length_bytes))

        if fragment_end <= total_len:
            # Full record fits
            fragment_bytes = payload[fragment_start:fragment_end]
            if fragment_bytes:
                segments.append(format_block(fragment_bytes))
            offset = fragment_end
        else:
            # Truncated record, use remaining bytes as fragment and stop
            fragment_bytes = payload[fragment_start:total_len]
            if fragment_bytes:
                segments.append(format_block(fragment_bytes))
            offset = total_len
            break

    # If any extra bytes remain that are smaller than a header, dump them
    if offset < total_len:
        remaining = payload[offset:]
        if remaining:
            segments.append(format_block(remaining))

    return " ".join(segments)


def main() -> None:
    args = parse_args()

    try:
        with open(args.target, "r", encoding="utf-8") as f:
            line_index = 0
            for raw_line in f:
                if args.count is not None and line_index >= args.count:
                    break

                line = raw_line.strip()
                if not line:
                    continue

                try:
                    payload_bytes = hex_line_to_bytes(line)
                except ValueError as e:
                    print(f"# Failed to parse line {line_index + 1}: {e}", file=sys.stderr)
                    line_index += 1
                    continue

                if not payload_bytes:
                    line_index += 1
                    continue

                # Decide type: STUN first, then DTLS, then SRTCP, otherwise SRTP
                if is_stun_packet(payload_bytes):
                    parsed = parse_stun_message(payload_bytes)
                elif is_dtls_packet(payload_bytes):
                    parsed = parse_dtls_records(payload_bytes)
                elif len(payload_bytes) >= 2 and is_rtcp_packet(payload_bytes[1]):
                    parsed = parse_srtcp_packet(payload_bytes)
                else:
                    parsed = parse_srtp_packet(payload_bytes)

                print(parsed)
                line_index += 1
    except FileNotFoundError:
        print(f"File not found: {args.target}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

