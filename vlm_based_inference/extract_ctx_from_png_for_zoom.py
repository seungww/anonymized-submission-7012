import argparse
import os
import sys
import json
import base64
from openai import OpenAI

API_KEY ""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def main():
    parser = argparse.ArgumentParser(description="Analyze a Zoom screenshot and generate status JSON and CI rules.")
    parser.add_argument("--image", required=True, help="Path to the Zoom screenshot image (e.g., zoom.png)")
    args = parser.parse_args()

    image_path = args.image

    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        sys.exit(1)

    base64_image = encode_image(image_path)
 
    prompt = """
You see a Zoom meeting screenshot.
Participants: Alice, Bob, Charlie, David, Emily, Fred.
If a name is not visible, set audio="unknown" and video="unknown".
If a name is visible, set audio="unmute" and video="low" by default.
If the video tile is a solid color with one capital letter, set video="off".
Layout rules: if all tiles are the same size, set video="medium" for all visible tiles except "off". If one tile is much larger, set that tile to video="high" and all other visible tiles to "low", except "off".
Audio rule: only if a mute icon is clearly visible, set audio="mute". Otherwise keep audio="unmute".
ONLY output a single JSON: {
"context": { "Alice": {"audio":"mute|unmute|unknown","video":"off|high|medium|low|unknown"}, "Bob": {...}, ...},
}
"""

    client = OpenAI(api_key=API_KEY)

    resp = client.responses.create(
        model="gpt-4o-mini", # $0.15
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}",},
            ],
        }],
    )

    raw_output = resp.output_text.strip()
    
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`") 
        if raw_output.startswith("json"):
            raw_output = raw_output[len("json"):].strip()
            
    data = json.loads(raw_output)
    
    base, _ = os.path.splitext(image_path)
    output_path = f"{base}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved JSON to {output_path}")

if __name__ == "__main__":
    main()

