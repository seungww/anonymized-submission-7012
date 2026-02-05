import os
import json
from pathlib import Path
import argparse

def fill_missing_frames(directory):
    path = Path(directory)
    json_files = sorted(path.glob("frame_*.json"))

    frame_indices = [int(f.stem.split("_")[1]) for f in json_files]
    frame_indices.sort()

    for i in range(len(frame_indices) - 1):
        current_idx = frame_indices[i]
        next_idx = frame_indices[i + 1]

        if next_idx - current_idx > 1:
            with open(path / f"frame_{current_idx:06d}.json") as f1, open(path / f"frame_{next_idx:06d}.json") as f2:
                data1 = json.load(f1)
                data2 = json.load(f2)

            if data1 == data2:
                for missing_idx in range(current_idx + 1, next_idx):
                    out_path = path / f"frame_{missing_idx:06d}.json"
                    with open(out_path, "w") as out_f:
                        json.dump(data1, out_f, indent=2)
                    print(f"Filled: {out_path.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill missing frame_XXXXXX.json files if content is identical between surrounding frames.")
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Target directory containing frame_XXXXXX.json files"
    )

    args = parser.parse_args()
    fill_missing_frames(args.target)

