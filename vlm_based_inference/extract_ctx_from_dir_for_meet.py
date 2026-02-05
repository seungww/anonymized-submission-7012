import argparse
import subprocess
import json
from pathlib import Path

def run_extract(image_path: Path):
    cmd = ["python", "extract_ctx_from_png_for_meet.py", "--image", str(image_path)]
    subprocess.run(cmd, check=True)
    print(f"Processed {image_path}")

def json_equal(file1: Path, file2: Path):
    if not file1.exists() or not file2.exists():
        return False
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        try:
            data1 = json.load(f1)
            data2 = json.load(f2)
        except json.JSONDecodeError:
            return False
    return data1 == data2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target directory containing frame PNG files")
    parser.add_argument("--all", action="store_true", help="Process all PNG files in order without skipping")
    args = parser.parse_args()

    target_dir = Path(args.target)
    png_files = sorted(target_dir.glob("frame_*.png"), key=lambda x: int(x.stem.split("_")[1]))

    if args.all:
        for png_file in png_files:
            run_extract(png_file)
        return

    prev_json = None
    prev_frame_idx = None

    for i in range(0, len(png_files), 10):
        current_png = png_files[i]
        current_idx = int(current_png.stem.split("_")[1])
        current_json = current_png.with_suffix(".json")

        run_extract(current_png)

        if prev_json is not None:
            same = json_equal(prev_json, current_json)
            print(f"Comparison Result: {'SAME' if same else 'DIFFERENT'}")
            if not same:
                start = prev_frame_idx + 1
                end = current_idx
                intermediate_frames = [p for p in png_files if start <= int(p.stem.split("_")[1]) < end]
                for frame_png in intermediate_frames:
                    run_extract(frame_png)

        prev_json = current_json
        prev_frame_idx = current_idx

if __name__ == "__main__":
    main()

