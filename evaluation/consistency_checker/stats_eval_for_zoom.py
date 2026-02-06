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

def parse_user_line(s: str) -> List[Token]:
    toks = [parse_tok(tok) for tok in re.split(r"[,\s]+", s.strip()) if tok.strip()]
    return [t for t in toks if t]

def is_self_triple(t: Token) -> bool:
    a, b, c = t[0].lower(), t[1].lower(), t[2].lower()
    return a == b == c

def base_val(v_opt: Optional[str]) -> str:
    return (v_opt or "on").lower()

def net_values(tt: str, v: str) -> List[str]:
    tt = tt.lower()
    v = v.lower()
    if tt == "video":
        return ["high", "medium", "low"] if v == "on" else [v]
    if tt == "audio":
        return ["unmute"] if v == "on" else [v]
    return [v]

def user_accept_video(v: str) -> List[str]:
    v = v.lower()
    if v == "on":
        return ["high", "medium", "low"]
    if v in ("high", "medium", "low"):
        return [v]
    return []

def classify_labeled_match(net_item: Token, user_items: List[Token]) -> bool:
    ns, nr, nj, nt, nv = net_item
    ntl = nt.lower()
    n_base = base_val(nv)
    n_vals = net_values(ntl, n_base)

    candidates = [
        u for u in user_items
        if u[3].lower() == ntl
        and (u[0].lower(), u[1].lower(), u[2].lower()) == (ns.lower(), nr.lower(), nj.lower())
    ]
    if not candidates:
        return False

    for us, ur, uj, ut, uv in candidates:
        u_base = base_val(uv)

        if ntl == "video":
            if n_base in ("high", "medium", "low") and u_base in ("high", "medium", "low") and n_base == u_base:
                return True
            if any(v in user_accept_video(u_base) for v in n_vals):
                return True

        elif ntl == "audio":
            n_eff = "unmute" if n_base == "on" else n_base
            u_eff = "unmute" if u_base == "on" else u_base
            if n_eff == u_eff:
                return True

    return False

def token_to_key(t: Token) -> str:
    a, b, c, d, v = t
    return f"{a}_{b}_{c}_{d}_{v}" if v else f"{a}_{b}_{c}_{d}"

def bump(d: Dict[str, int], k: str) -> None:
    d[k] = d.get(k, 0) + 1

def print_counts(title: str, d: Dict[str, int]) -> None:
    if not d:
        return
    print(title)
    for k, v in sorted(d.items(), key=lambda x: (-x[1], x[0])):
        print(f"- {k}: {v}")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--limit", type=int, default=100000)
    args = ap.parse_args()

    net_lines = open(args.net, encoding="utf-8").readlines()
    user_lines = open(args.user, encoding="utf-8").readlines()
    n = min(len(net_lines), len(user_lines), args.limit)

    user_items_per_line = [parse_user_line(u) for u in user_lines[:n]]

    observed = n
    labeled = 0
    mismatched_control = 0
    mismatched_data = 0

    control_counts: Dict[str, int] = {}
    data_counts: Dict[str, int] = {}

    waiting_user_all_control = (args.client.lower() == "fred")

    for i in range(n):
        net_raw = net_lines[i].strip()
        if not net_raw:
            continue

        labeled += 1

        net_item = parse_tok(net_raw)
        if not net_item:
            if waiting_user_all_control:
                mismatched_control += 1
                bump(control_counts, net_raw)
            else:
                mismatched_data += 1
                bump(data_counts, net_raw)
            continue

        if is_self_triple(net_item):
            continue

        if classify_labeled_match(net_item, user_items_per_line[i]):
            continue

        if waiting_user_all_control:
            mismatched_control += 1
            bump(control_counts, token_to_key(net_item))
            continue

        _, rec, subj, _, _ = net_item
        if rec and subj and rec.lower() == subj.lower():
            mismatched_control += 1
            bump(control_counts, token_to_key(net_item))
        else:
            mismatched_data += 1
            bump(data_counts, token_to_key(net_item))

    print("Observed:", observed)
    print("Labeled:", labeled)
    print("Mismatched(Control):", mismatched_control)
    print("Mismatched(Data):", mismatched_data)

    print_counts("Mismatched(Control) breakdown:", control_counts)
    print_counts("Mismatched(Data) breakdown:", data_counts)

if __name__ == "__main__":
    main()

