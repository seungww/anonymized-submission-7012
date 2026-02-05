import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_context(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    ctx = doc.get("context", {})
    if not isinstance(ctx, dict):
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for person, vv in ctx.items():
        out[str(person)] = vv if isinstance(vv, dict) else {}
    return out


def norm_value(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


@dataclass
class FieldStats:
    match: int = 0
    mismatch: int = 0
    missing_value_in_adj: int = 0
    missing_value_in_ori: int = 0


@dataclass
class CompareResult:
    people_total: int
    people_exact_match: int
    people_with_any_diff: int
    audio: FieldStats
    video: FieldStats
    diffs: List[Tuple[str, str, Optional[str], Optional[str]]]


@dataclass
class GlobalStats:
    files_total: int = 0
    files_matched: int = 0
    files_mismatched: int = 0
    files_missing_in_adj: int = 0
    audio: FieldStats = FieldStats()
    video: FieldStats = FieldStats()


def compare_docs(adj_doc: Dict[str, Any], ori_doc: Dict[str, Any]) -> CompareResult:
    adj = extract_context(adj_doc)
    ori = extract_context(ori_doc)

    people = sorted(adj.keys())
    audio_stats = FieldStats()
    video_stats = FieldStats()
    diffs: List[Tuple[str, str, Optional[str], Optional[str]]] = []

    people_exact_match = 0
    people_with_any_diff = 0

    for person in people:
        a = adj.get(person, {})
        o = ori.get(person, {})

        person_diff = False

        for field, stats in (("audio", audio_stats), ("video", video_stats)):
            av = norm_value(a.get(field))
            ov = norm_value(o.get(field))

            if av is None:
                stats.missing_value_in_adj += 1
                if av != ov:
                    diffs.append((person, field, av, ov))
                    person_diff = True
                continue

            if ov is None:
                stats.missing_value_in_ori += 1
                diffs.append((person, field, av, ov))
                person_diff = True
                continue

            if av == ov:
                stats.match += 1
            else:
                stats.mismatch += 1
                diffs.append((person, field, av, ov))
                person_diff = True

        if not person_diff:
            people_exact_match += 1
        else:
            people_with_any_diff += 1

    return CompareResult(
        people_total=len(people),
        people_exact_match=people_exact_match,
        people_with_any_diff=people_with_any_diff,
        audio=audio_stats,
        video=video_stats,
        diffs=diffs,
    )


def add_fieldstats(dst: FieldStats, src: FieldStats) -> None:
    dst.match += src.match
    dst.mismatch += src.mismatch
    dst.missing_value_in_adj += src.missing_value_in_adj
    dst.missing_value_in_ori += src.missing_value_in_ori


def fmt_fieldstats(name: str, s: FieldStats) -> str:
    return (
        f"{name}: match={s.match}, mismatch={s.mismatch}, "
        f"missing_value_in_adj={s.missing_value_in_adj}, missing_value_in_ori={s.missing_value_in_ori}"
    )


def print_file_diff(title: str, res: CompareResult, max_diffs: int) -> None:
    print(f"== {title} ==")
    print(f"people_total={res.people_total}")
    print(f"people_exact_match={res.people_exact_match}")
    print(f"people_with_any_diff={res.people_with_any_diff}")
    print(fmt_fieldstats("audio", res.audio))
    print(fmt_fieldstats("video", res.video))

    shown = res.diffs[:max_diffs] if max_diffs >= 0 else res.diffs
    print(f"diffs({len(res.diffs)}):")
    for person, field, av, ov in shown:
        print(f"- {person}.{field}: adj={av!r} ori={ov!r}")
    if max_diffs >= 0 and len(res.diffs) > max_diffs:
        print(f"... ({len(res.diffs) - max_diffs} more)")


def list_json_files_under(root: str) -> List[str]:
    out: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".json"):
                out.append(os.path.join(dirpath, fn))
    out.sort()
    return out


def compare_dirs(adj_dir: str, ori_dir: str, max_diffs: int) -> int:
    ori_files = list_json_files_under(ori_dir)
    g = GlobalStats(files_total=len(ori_files))
    any_printed = False

    for ori_full in ori_files:
        rel = os.path.relpath(ori_full, ori_dir)
        adj_full = os.path.join(adj_dir, rel)

        if not os.path.exists(adj_full):
            g.files_missing_in_adj += 1
            print(f"== {rel} ==")
            print("missing_in_adj_dir")
            any_printed = True
            continue

        adj_doc = load_json(adj_full)
        ori_doc = load_json(ori_full)
        res = compare_docs(adj_doc, ori_doc)

        add_fieldstats(g.audio, res.audio)
        add_fieldstats(g.video, res.video)

        if res.people_with_any_diff == 0:
            g.files_matched += 1
        else:
            g.files_mismatched += 1
            print_file_diff(rel, res, max_diffs)
            any_printed = True

    print("== GLOBAL SUMMARY ==")
    print(f"files_total={g.files_total}")
    print(f"files_matched={g.files_matched}")
    print(f"files_mismatched={g.files_mismatched}")
    print(f"files_missing_in_adj={g.files_missing_in_adj}")
    print(fmt_fieldstats("audio_total", g.audio))
    print(fmt_fieldstats("video_total", g.video))

    if g.files_missing_in_adj > 0:
        return 2
    if g.files_mismatched > 0:
        return 1
    return 0


def compare_files(adj_path: str, ori_path: str, max_diffs: int) -> int:
    adj_doc = load_json(adj_path)
    ori_doc = load_json(ori_path)
    res = compare_docs(adj_doc, ori_doc)

    if res.people_with_any_diff > 0:
        print_file_diff(f"{os.path.basename(adj_path)} vs {os.path.basename(ori_path)}", res, max_diffs)
        return 1

    print("== FILE SUMMARY ==")
    print("matched")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--adj", required=True)
    p.add_argument("--ori", required=True)
    p.add_argument("--max-diffs", type=int, default=200)
    return p


def main() -> None:
    args = build_parser().parse_args()

    adj_is_dir = os.path.isdir(args.adj)
    ori_is_dir = os.path.isdir(args.ori)

    if adj_is_dir and ori_is_dir:
        raise SystemExit(compare_dirs(args.adj, args.ori, args.max_diffs))

    if adj_is_dir != ori_is_dir:
        print("error: both --adj and --ori must be files or both must be directories")
        raise SystemExit(2)

    raise SystemExit(compare_files(args.adj, args.ori, args.max_diffs))


if __name__ == "__main__":
    main()

