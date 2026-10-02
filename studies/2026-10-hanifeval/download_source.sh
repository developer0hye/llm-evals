#!/usr/bin/env bash
# Fetch the English source (google/IFEval, Apache-2.0) at a pinned revision and verify SHA-256.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
f=data/ifeval_input_data.jsonl
[ -f "$f" ] || curl -fsSL -o "$f" "https://huggingface.co/datasets/google/IFEval/resolve/966cd89545d6b6acfd7638bc708b98261ca58e84/ifeval_input_data.jsonl"
echo "6a85310ca8ce15eff755aa08a3a4ff931c7e273e7515ebb3c492ea85fd8288f2  $f" | sha256sum -c --quiet - && echo "verified $f"
