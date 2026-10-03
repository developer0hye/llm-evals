#!/usr/bin/env bash
# Assemble the Hugging Face dataset repo (developer0hye/HanIFEval) into $1 from this study's files.
#   bash hf/build.sh /tmp/hanifeval_hf && hf upload developer0hye/HanIFEval /tmp/hanifeval_hf . --repo-type dataset --exclude "**/__pycache__/**"
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
out="${1:?usage: build.sh <out_dir>}"
rm -rf "$out" && mkdir -p "$out/data" "$out/checker"
cp "$here/hf/README.md" "$here/hf/NOTICE" "$here/hf/score.py" "$out/"
cp "$here/../../LICENSE" "$out/LICENSE"
cp "$here/release/hanifeval_v1.jsonl" "$here/release/hanifeval_v1.1.jsonl" "$out/data/"
cp "$here/release/provenance.json" "$out/"
cp "$here"/checker/*.py "$out/checker/"
find "$out" -name __pycache__ -prune -exec rm -rf {} +
echo "built $out:"; (cd "$out" && find . -type f | sort)
