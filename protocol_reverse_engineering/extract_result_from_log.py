import argparse
import re

def extract_values(path):
    pattern = re.compile(r"ByteF\s+\d+:\s*(.*)")
    results = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                results.append(m.group(1).strip())

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    extracted = extract_values(args.target)

    for item in extracted:
        print(item)


if __name__ == "__main__":
    main()
