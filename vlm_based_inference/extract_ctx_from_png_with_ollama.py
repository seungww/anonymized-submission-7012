#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path


def read_prompt(prompt_arg: str) -> str:
    p = Path(prompt_arg)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return prompt_arg  # treat as literal prompt string


def call_ollama_generate(host: str, model: str, prompt: str, image_path: Path, temperature: float = 0.0):
    img_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    url = host.rstrip("/") + "/api/generate"
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=1200) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTPError {e.code}: {e.reason}\n{err_body}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to call Ollama at {url}: {e}") from e


def main():
    parser = argparse.ArgumentParser(description="Run Ollama qwen3-vl on an image and save JSON output.")
    parser.add_argument("--input", "-i", required=True, help="Path to input image (.png recommended).")
    parser.add_argument("--prompt", "-p", required=True, help="Prompt text OR a path to a prompt file.")
    parser.add_argument("--model", "-m", default="qwen3-vl:8b", help="Ollama model tag (default: qwen3-vl:8b).")
    parser.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
                        help="Ollama host URL (default: env OLLAMA_HOST or http://localhost:11434).")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature (default: 0.0).")
    args = parser.parse_args()

    image_path = Path(args.input).expanduser().resolve()
    if not image_path.exists() or not image_path.is_file():
        print(f"ERROR: input not found: {image_path}", file=sys.stderr)
        sys.exit(2)

    if image_path.suffix.lower() != ".png":
        # You asked for .png, but we won't hard-fail; just warn.
        print(f"WARNING: input extension is {image_path.suffix}, not .png", file=sys.stderr)

    prompt = read_prompt(args.prompt)

    resp = call_ollama_generate(
        host=args.host,
        model=args.model,
        prompt=prompt,
        image_path=image_path,
        temperature=args.temperature,
    )

    # Ollama /api/generate typically returns {"response": "...", ...}
    output = {
        "input": str(image_path),
        "model": args.model,
        "prompt": prompt,
        "response": resp.get("response", ""),
        "ollama_raw": resp,  # keep full raw response for debugging
    }

    out_path = image_path.with_suffix(".json")
    out_path.write_text(resp.get("response", ""))
    print(str(out_path))


if __name__ == "__main__":
    main()
