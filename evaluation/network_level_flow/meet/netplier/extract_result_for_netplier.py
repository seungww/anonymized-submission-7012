import argparse

def normalize_hex_line(line):
    cleaned = line.replace('-', '')
    parts = cleaned.split()
    upper_hex = [p.upper() for p in parts]
    return ' '.join(upper_hex)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True)
    args = parser.parse_args()

    with open(args.target, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            print(normalize_hex_line(line))

if __name__ == '__main__':
    main()
