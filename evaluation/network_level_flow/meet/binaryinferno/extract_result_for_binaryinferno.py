import argparse


def load_rule(rule_path: str) -> list[int]:
    with open(rule_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.replace("|", " ")
            tokens = line.split()
            return [len(tok) for tok in tokens]
    raise ValueError("Invalid rule file")


def format_with_rule(hex_str: str, rule_lengths: list[int]) -> str:
    s = hex_str.strip()
    if not s:
        return ""

    idx = 0
    parts: list[str] = []

    for length in rule_lengths:
        if idx >= len(s):
            break

        remain = len(s) - idx

        if remain <= length:
            parts.append(s[idx:])
            idx = len(s)
            break

        parts.append(s[idx:idx + length])
        idx += length

    if idx < len(s):
        parts.append(s[idx:])

    return " ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule", required=True, help="rule file path")
    parser.add_argument("--target", required=True, help="target file path")
    args = parser.parse_args()

    rule_lengths = load_rule(args.rule)

    with open(args.target, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            formatted = format_with_rule(line, rule_lengths)
            print(formatted)


if __name__ == "__main__":
    main()
