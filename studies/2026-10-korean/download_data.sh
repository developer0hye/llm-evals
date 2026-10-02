#!/usr/bin/env bash
# Fetch the four evaluation sets at pinned revisions and verify SHA-256.
# None of the data is committed (licences: KoBALT CC BY-NC 4.0, KoSimpleQA CC BY 4.0,
# KLUE CC BY-SA 4.0, LBox Open CC BY-NC 4.0; see ../../NOTICE).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
fetch() {  # url  file  sha256
  [ -f "data/$2" ] || curl -fsSL -o "data/$2" "$1"
  echo "$3  data/$2" | sha256sum -c --quiet - || { echo "SHA-256 mismatch: data/$2" >&2; exit 1; }
}
HF=https://huggingface.co/datasets
GH=https://raw.githubusercontent.com
fetch "$HF/snunlp/KoBALT-700/resolve/30c30a431066508e6bef77cfa6d6059b85b12f0d/data/train.jsonl" \
  kobalt.jsonl ecc68805e17d1c87b63cbb70ec3ba101eabcbd2c489e813ba229f272f20c092f
fetch "$HF/snunlp/KoBALT-700/resolve/30c30a431066508e6bef77cfa6d6059b85b12f0d/evaluation_protocol.md" \
  kobalt_evaluation_protocol.md 9f2a2b5cdc8758dc361d1ad376c829785bc4fe9cf7df4a415ba3e98e48cd0388
fetch "$GH/naver-ai/KoSimpleQA/1bdbb613c39973538239a161ea2425d763b25fe8/updated_kosimpleqa_with_trans.json" \
  kosimpleqa.json 4d6d41c70dcffc32a794c454fb832eb0088ea63bc3c99c1009f04fbd49ab68a8
fetch "$GH/KLUE-benchmark/KLUE/3efd98708a40ff49251fddde35453f8fbb11f536/klue_benchmark/klue-ner-v1.1/klue-ner-v1.1_dev.tsv" \
  klue-ner-v1.1_dev.tsv 0f4d5e818f7b82d299c3a87856fc40a706f5943207580ddb252397e387050a54
fetch "$HF/lbox/lbox_open/resolve/10429acf7e13d7ef2ea4187ffbd685490289a82c/casename_classification/test.jsonl" \
  lbox_casename_test.jsonl e4095da9314786bd7ca782f02e729b8ad2129f809643794d594f07079fcd8d25
echo "all 5 files present and verified in data/"
