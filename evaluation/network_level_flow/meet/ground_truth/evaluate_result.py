#!/usr/bin/env python3
import argparse


def get_base_and_boundaries(line: str):
    """
    Given a line with spaces as separators, return:
      - base string without spaces
      - a set of boundary positions (indices between characters in base)
        where a space existed in the original line.
    Example:
      line = "90 78 EB1B"
      tokens = ["90", "78", "EB1B"]
      base   = "9078EB1B"
      boundaries = {2, 4}  # between 90|78 and 9078|EB1B
    """
    # Remove newline characters only, keep internal spaces
    line = line.rstrip("\n\r")

    tokens = line.split()
    if not tokens:
        return "", set()

    base = "".join(tokens)

    boundaries = set()
    pos = 0
    # For each token boundary except the last token
    for token in tokens[:-1]:
        pos += len(token)
        boundaries.add(pos)

    return base, boundaries


def main():
    parser = argparse.ArgumentParser(
        description="Compare whitespace positions between ground and target files."
    )
    parser.add_argument(
        "--ground",
        required=True,
        help="Path to ground truth file",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to target prediction file",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding for both files (default: utf-8)",
    )

    args = parser.parse_args()

    # Global counters
    total_lines = 0
    compared_lines = 0
    base_mismatch_lines = 0

    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    total_positions = 0  # total candidate positions considered

    with open(args.ground, encoding=args.encoding) as f_ground, \
            open(args.target, encoding=args.encoding) as f_target:
                
        for g_line, t_line in zip(f_ground, f_target):
            total_lines += 1

            base_g, boundaries_g = get_base_and_boundaries(g_line)
            base_t, boundaries_t = get_base_and_boundaries(t_line)

            prefix_len = 0
            for cg, ct in zip(base_g, base_t):
                if cg == ct:
                    prefix_len += 1
                else:
                    break

            if prefix_len == 0:
                base_mismatch_lines += 1
                print(g_line)
                print(t_line)
                continue

            g_restricted = {p for p in boundaries_g if p <= prefix_len}
            t_restricted = {p for p in boundaries_t if p <= prefix_len}

            if not g_restricted:
                continue

            compared_lines += 1

            cutoff = max(g_restricted)

            # Include encrypted parts
            # cutoff = prefix_len

            g_restricted = {p for p in g_restricted if p <= cutoff}
            t_restricted = {p for p in t_restricted if p <= cutoff}

            line_positions = cutoff

            tp = len(g_restricted & t_restricted)
            fp = len(t_restricted - g_restricted)
            fn = len(g_restricted - t_restricted)
            tn = line_positions - tp - fp - fn

            total_tp += tp
            total_fp += fp
            total_fn += fn
            total_tn += tn
            total_positions += line_positions

    # Compute metrics
    def safe_ratio(num, den):
        return float(num) / den if den > 0 else float("nan")

    precision = safe_ratio(total_tp, total_tp + total_fp)
    recall = safe_ratio(total_tp, total_tp + total_fn)
    f1 = safe_ratio(2 * total_tp, 2 * total_tp + total_fp + total_fn)
    accuracy = safe_ratio(total_tp + total_tn, total_positions)
    fp_rate = safe_ratio(total_fp, total_fp + total_tn)  # on negative positions

    # Print summary
    print("=== Segmentation statistics ===")
    print(f"Total lines read (paired):          {total_lines}")
    print(f"Lines actually compared:            {compared_lines}")
    print(f"Lines skipped due to base mismatch: {base_mismatch_lines}")
    print()
    print(f"Total positions considered: {total_positions}")
    print(f"True positives (TP):        {total_tp}")
    print(f"False positives (FP):       {total_fp}")
    print(f"False negatives (FN):       {total_fn}")
    print(f"True negatives (TN):        {total_tn}")
    print()
    print("=== Metrics ===")
    print(f"Precision (TP / (TP + FP)):          {precision:.4f}")
    print(f"Recall    (TP / (TP + FN)):          {recall:.4f}")
    print(f"F1 score:                            {f1:.4f}")
    print(f"Accuracy ((TP + TN) / All positions): {accuracy:.4f}")
    print(f"False positive rate (FP / (FP + TN)): {fp_rate:.44f}")


if __name__ == "__main__":
    main()
