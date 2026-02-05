import argparse
import re
from typing import Optional, Tuple, List, Dict

Token = Tuple[str, str, str, str, Optional[str]]

def parse_tok(s: str) -> Optional[Token]:
    s = s.strip()
    if not s:
        return None
    parts = s.split("_")
    if len(parts) < 4:
        return None
    return parts[0], parts[1], parts[2], parts[3], (parts[4] if len(parts) >= 5 else None)

def is_self_triple(t: Token) -> bool:
    a, b, c = t[0].lower(), t[1].lower(), t[2].lower()
    return a == b == c

def base_val(t: str, v_opt: Optional[str]) -> str:
    return (v_opt or "on").lower()

def net_values(t: str, v: str) -> List[str]:
    t = t.lower()
    v = v.lower()
    if t == "video":
        return ["high", "medium", "low"] if v == "on" else [v]
    if t == "audio":
        return ["unmute"] if v == "on" else [v]
    return [v]

def user_accept_video(v: str) -> List[str]:
    v = v.lower()
    if v == "on":
        return ["high", "medium", "low"]
    if v == "high":
        return ["high"]
    if v == "medium":
        return ["high"]
    if v == "low":
        return ["low"]
    return []

def classify_on_items(net_item: Token, user_items: List[Token]) -> Tuple[Optional[str], str]:
    """
    Return:
      - 'PERFECT'
      - 'PARTIAL'
      - None  (no match)
    """
    ns, nr, nj, nt, nv = net_item
    ntl = nt.lower()
    n_base = base_val(nt, nv)
    n_vals = net_values(ntl, n_base)

    candidates = [
        u for u in user_items
        if u and u[3].lower() == ntl
        and (u[0].lower(), u[1].lower(), u[2].lower()) == (ns.lower(), nr.lower(), nj.lower())
    ]
    if not candidates:
        return None, "no triple match"

    for us, ur, uj, ut, uv in candidates:
        u_base = base_val(ut, uv)

        if ntl == "video":
            if (
                n_base in ("high", "medium", "low")
                and u_base in ("high", "medium", "low")
                and n_base == u_base
            ):
                return "PERFECT", f"video exact match {n_base}"

            if any(v in user_accept_video(u_base) for v in n_vals):
                return "PARTIAL", f"video acceptable range {n_vals} vs user {u_base}"

        elif ntl == "audio":
            n_eff = "unmute" if n_base == "on" else n_base
            u_eff = "unmute" if u_base == "on" else u_base
            if n_eff == u_eff:
                if n_base != "on" and u_base != "on":
                    return "PERFECT", f"audio exact match {n_eff}"
                return "PARTIAL", (
                    f"audio mapped via on ({n_base}->{n_eff}, {u_base}->{u_eff})"
                )

    return None, "value mismatch"

def parse_user_line(s: str) -> List[Token]:
    tokens = [parse_tok(tok) for tok in re.split(r"[,\s]+", s.strip()) if tok.strip()]
    return [t for t in tokens if t]

def debug_log(enabled: bool, line_no: int, tag: str, message: str) -> None:
    if enabled:
        print(f"[{line_no:04d}] {tag}: {message}")

def token_to_key(t: Token) -> str:
    """Convert token to output key like Alice_Bob_Charlie_video_high."""
    a, b, c, d, v = t
    if v:
        return f"{a}_{b}_{c}_{d}_{v}"
    return f"{a}_{b}_{c}_{d}"

def main():
    ap = argparse.ArgumentParser(
        description="Compare net/user entries with PERFECT/PARTIAL match and Case classification."
    )
    ap.add_argument("--net", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--limit", type=int, default=1000000)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    net_lines = open(args.net, encoding="utf-8").readlines()
    user_lines = open(args.user, encoding="utf-8").readlines()
    n = min(len(net_lines), len(user_lines), args.limit)

    user_items_per_line = [parse_user_line(u) for u in user_lines[:n]]

    total = n
    empty = 0
    found_triple = 0
    found_perfect = 0
    found_partial = 0
    case1 = 0
    case2 = 0
    others = 0

    others_count: Dict[str, int] = {}

    for i in range(n):
        ln = i + 1
        net_raw = net_lines[i].strip()

        if not net_raw:
            empty += 1
            debug_log(args.debug, ln, "EMPTY", "net line empty")
            continue

        net_item = parse_tok(net_raw)
        if not net_item:
            others += 1
            others_count[net_raw] = others_count.get(net_raw, 0) + 1
            debug_log(args.debug, ln, "INVALID", f"cannot parse net='{net_raw}'")
            continue

        if is_self_triple(net_item):
            found_triple += 1
            debug_log(args.debug, ln, "TRIPLE", f"net='{net_raw}'")
            continue

        user_items = user_items_per_line[i]
        kind, reason = classify_on_items(net_item, user_items)

        if kind == "PERFECT":
            found_perfect += 1
            debug_log(args.debug, ln, "PERFECT", f"net='{net_raw}' {reason}")
            continue

        if kind == "PARTIAL":
            found_partial += 1
            debug_log(args.debug, ln, "PARTIAL", f"net='{net_raw}' {reason}")
            continue

        _, rec, subj, _, _ = net_item
        if rec and subj and rec.lower() == subj.lower():
            if rec.lower() == args.client.lower():
                case1 += 1
                debug_log(args.debug, ln, "CASE1", f"net='{net_raw}'")
            else:
                case2 += 1
                debug_log(args.debug, ln, "CASE2", f"net='{net_raw}'")
            continue

        others += 1
        key = token_to_key(net_item)
        others_count[key] = others_count.get(key, 0) + 1
        debug_log(args.debug, ln, "OTHERS", f"net='{net_raw}'")

    print("Total:", total)
    print("Empty:", empty)
    print("Found TRIPLE:", found_triple)
    print("Found PERFECT:", found_perfect)
    print("Found PARTIAL:", found_partial)
    print("Case 1:", case1)
    print("Case 2:", case2)
    print("Others:", others)

    for k, v in sorted(others_count.items(), key=lambda x: -x[1]):
        print(f"- {k}: {v}")

if __name__ == "__main__":
    main()

