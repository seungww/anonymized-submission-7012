# UNVEIL: UI-Network Consistency Checker for VCA Privacy

This repository contains research artifacts for **UNVEIL**, a dynamic testing pipeline that reconstructs (i) UI-implied, user-aware information flows and (ii) network-level information flows, and flags mismatches as potential privacy violations.

## Repository Structure

- `multimodal_data_collection/`
  Automation scripts and media injection assets to collect synchronized **screen recordings** and **packet traces** for Zoom and Google Meet.

- `vlm_based_inference/`
  VLM-based extraction of per-participant UI context (e.g., audio/video states) and conversion into user-aware flows.

- `protocol_reverse_engineering/`
  Preprocessing of pcaps, byte-level structure inference (ByteBERT utilities), and CI-like semantic extraction from network traces.

- `evaluation/`
  End-to-end evaluation artifacts and results:
  - `experimental_setup/`: example session outputs (pcap/mp4/logs/hex) per participant
  - `user_aware_flow/`: UI-context diffs and summaries
  - `network_level_flow/`: baseline comparisons (NetPlier/BinaryInferno) and our results
  - `consistency_checker/`: `.user`, `.net`, and `.result` files for Zoom and Google Meet sessions

- `wireshark_zoom_dissector/`
  Wireshark Lua dissector plugin for Zoom protocol analysis.

## Typical Workflow

1. **Collect data** (`multimodal_data_collection/`)
   Produce synchronized artifacts such as `tcpdump_*.pcap`, `record_*.mp4`, and action logs.

2. **Infer UI context** (`vlm_based_inference/`)
   Extract UI state from recordings (or sampled frames) and generate user-aware flow representations.

3. **Derive network-level flows** (`protocol_reverse_engineering/`)
   Preprocess pcaps into hex and infer packet structure/semantics to build network-level flow representations.

4. **Run consistency checking** (`evaluation/consistency_checker/`)
   Compare `.user` (UI-derived) vs `.net` (network-derived) flows and output `.result` (mismatch candidates).

## Key Output Files (as used under `evaluation/`)

- `*.user`  : user-aware flow set derived from UI context  
- `*.net`   : network-level flow set derived from packet traces  
- `*.result`: detected mismatches between `.user` and `.net`
- All results mentioned in the Evaluation section can be found in the `evaluation/` directory.

## Example Usage

### Generate a `.ui` file from UI images
```bash
python vlm_based_inference/extract_labels_from_ui.py \
    --pcap ./evaluation/experimental_setup/zoom/recordings_tmv-red/preprocessed_tcpdump_20251230_103245.pcap \
    --target evaluation/experimental_setup/zoom/recordings_tmv-red/record_20251230_103245_adj
```

### Generate a `.net` file from packet traces
```bash
python protocol_reverse_engineering/extract_ci_from_hex_for_zoom.py \
    --hex evaluation/experimental_setup/zoom/recordings_tmv-red/preprocessed_tcpdump_20251230_103245.hex \
    --client Alice \
    --usermap evaluation/experimental_setup/zoom/usermap_recordings_20251230.json
```

### Run the consistency checker on a Zoom session

```bash
python evaluation/consistency_checker/stats_eval_for_zoom.py \
    --user evaluation/consistency_checker/zoom/recordings_tmv-red/20251230_103245.user \
    --net evaluation/consistency_checker/zoom/recordings_tmv-red/20251230_103245.net \
    --client Alice
```

## Notes

- The repository contains both **Zoom** and **Google Meet** pipelines, reflecting differences between proprietary and RTP/RTCP-based traffic.
- Server identifiers correspond to participants as follows:
  `red=Alice`, `green=Bob`, `blue=Charlie`, `cyan=David`, `magenta=Emily`, `yellow=Fred`.
- In `.net` files, when multimedia data is broadcast to all participants in a meeting room, the sender and recipient are set to the same name for convenience.
- Some subdirectories (e.g., `evaluation/network_level_flow/*/netplier` and `binaryinferno`) include baseline tooling/results for boundary inference comparisons.
- Due to repository size constraints, some files (e.g., videos and images) are not included in this repository snapshot.
