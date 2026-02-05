import argparse
import os
import json

USER_MAP = {}

VALUE_MAP = {
    '0': 'low',
    '1': 'medium',
    '2': 'high'
}

def get_value_from_nibble(byte_str):
    return VALUE_MAP.get(byte_str[1], None)


def get_usermap_path_from_hex(hex_path: str) -> str:
    hex_dir = os.path.dirname(os.path.abspath(hex_path))
    parent_dir = os.path.dirname(hex_dir)
    parent_name = os.path.basename(parent_dir)

    if not parent_name:
        parent_name = "default"

    filename = f"usermap_{parent_name}.json"
    return os.path.join(parent_dir, filename)


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


def get_user(tokens, start_idx):
    if start_idx >= len(tokens):
        return ""
    end_idx = start_idx + 4
    if end_idx > len(tokens):
        key = ''.join(tokens[start_idx:]).upper()
    else:
        key = ''.join(tokens[start_idx:end_idx]).upper()
    return USER_MAP.get(key, key)


def parse_line(tokens, args):
    if tokens[0] != '05':
        return ""

    results = []
    byte8 = tokens[7]
    byte9 = tokens[8]
    byte16 = tokens[15] if len(tokens) > 15 else None

    sender = recipient = subject = typ = value = None

    if byte8 in ['00', '01']:
        sender = args.client
    if byte8 in ['04', '05']:
        recipient = args.client

    def process_case(subject_idx, value_idx=None, type_str=None,
                     fixed_value=None, is_sender=False, is_recipient=False):
        nonlocal sender, recipient, subject, value, typ
        try:
            subject = get_user(tokens, subject_idx)
        except Exception:
            return None
        typ = type_str
        if fixed_value:
            value = fixed_value
        elif value_idx is not None:
            value = get_value_from_nibble(tokens[value_idx])
        if is_sender:
            sender = subject
        if is_recipient:
            recipient = subject
        if sender and recipient and subject and typ and value:
            return f"{sender}_{recipient}_{subject}_{typ}_{value}"
        elif sender and recipient and subject and typ:
            return f"{sender}_{recipient}_{subject}_{typ}"
        return None

    if byte8 == '00':
        if byte9 == '10':
            results.append(process_case(40, 54, 'video', is_recipient=True))
        elif byte9 == '0F':
            results.append(process_case(35, None, 'audio', fixed_value='unmute', is_recipient=True))
        elif byte9 == '21':
            results.append(process_case(28, None, 'video', fixed_value='on', is_recipient=True))
        elif byte9 == '22':
            results.append(process_case(28, None, 'audio', fixed_value='unmute', is_recipient=True))
        elif byte9 == '20':
            sender = get_user(tokens, 14)
            results.append(process_case(21, 27, 'video', is_recipient=True))

    elif byte8 == '01':
        if byte16 == '10':
            results.append(process_case(47, 61, 'video', is_recipient=True))
        elif byte16 == '0F':
            results.append(process_case(42, None, 'audio', fixed_value='unmute', is_recipient=True))
        elif byte16 == '21':
            results.append(process_case(35, None, 'video', fixed_value='on', is_recipient=True))
        elif byte16 == '22':
            results.append(process_case(35, None, 'audio', fixed_value='unmute', is_recipient=True))
        elif byte16 == '20':
            results.append(process_case(28, 34, 'video', is_recipient=True))

    elif byte8 == '04':
        if byte9 == '10':
            if tokens[23] in ['06', '0F']:
                results.append(process_case(42, 65, 'video', is_sender=True))
            else:
                results.append(process_case(40, 54, 'video', is_sender=True))
        elif byte9 == '0F':
            results.append(process_case(35, None, 'audio', fixed_value='unmute', is_sender=True))
        elif byte9 == '21':
            results.append(process_case(28, None, 'video', fixed_value='on', is_sender=True))
        elif byte9 == '22':
            results.append(process_case(28, None, 'audio', fixed_value='unmute', is_sender=True))
        elif byte9 == '20':
            sender = get_user(tokens, 14)
            results.append(process_case(21, 27, 'video', is_sender=False))

    elif byte8 == '05':
        if byte16 == '10':
            results.append(process_case(47, 61, 'video', is_sender=True))
        elif byte16 == '0F':
            results.append(process_case(42, None, 'audio', fixed_value='unmute', is_sender=True))
        elif byte16 == '21':
            results.append(process_case(35, None, 'video', fixed_value='on', is_sender=True))
        elif byte16 == '22':
            results.append(process_case(35, None, 'audio', fixed_value='unmute', is_sender=True))
        elif byte16 == '20':
            sender = get_user(tokens, 21)
            results.append(process_case(28, 34, 'video', is_sender=False))

    return ', '.join(filter(None, results)) if results else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hex', type=str, required=True)
    parser.add_argument('--client', type=str, required=True)
    parser.add_argument('--usermap', type=str, required=False,
                        help='Optional path to usermap file')
    args = parser.parse_args()

    if args.usermap:
        usermap_path = args.usermap
    else:
        usermap_path = get_usermap_path_from_hex(args.hex)

    global USER_MAP
    USER_MAP = load_usermap(usermap_path)

    with open(args.hex, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) < 30:
                print("")
                continue
            print(parse_line(tokens, args))


if __name__ == '__main__':
    main()

