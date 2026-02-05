import json
import argparse
from pathlib import Path

def generate_ui_file(json_path, client_name):
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")

    with open(path, 'r') as f:
        data = json.load(f)

    context = data.get("context", {})
    if client_name not in context:
        raise ValueError(f"Client '{client_name}' not found in context.")

    parameters = []
    client_state = context[client_name]
    other_users = [user for user in context if user != client_name]

    # 1. Client → Others
    for recipient in other_users:
        recipient_state = context[recipient]
        is_recipient_unknown = (
            recipient_state.get("audio", "unknown") == "unknown" and
            recipient_state.get("video", "unknown") == "unknown"
        )

        for attr_type in ["audio", "video"]:  # order: audio then video
            parameters.append({
                "subject": client_name,
                "sender": client_name,
                "recipient": recipient,
                "type": attr_type,
                "value": "unknown" if is_recipient_unknown else client_state.get(attr_type, "unknown")
            })

    # 2. Others → Client
    for subject in other_users:
        subject_state = context[subject]
        for attr_type in ["audio", "video"]:  # order: audio then video
            parameters.append({
                "subject": subject,
                "sender": subject,
                "recipient": client_name,
                "type": attr_type,
                "value": subject_state.get(attr_type, "unknown")
            })

    output_data = {
        "parameters": parameters
    }

    output_path = path.with_suffix(".ui")
    with open(output_path, "w") as out_f:
        json.dump(output_data, out_f, indent=2)

    print(f"UI file saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate .ui file for contextual integrity analysis.")
    parser.add_argument("--target", required=True, help="Path to input frame_XXXXXX.json file")
    parser.add_argument("--client", required=True, help="Name of the UI client (recipient)")
    args = parser.parse_args()

    generate_ui_file(args.target, args.client)

