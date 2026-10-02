#!/usr/bin/env python3
"""Translate google/IFEval items into Korean with Gemini 3.1 Pro, following translation_guideline.md.

Usage (from this directory, OPENROUTER_API_KEY set):
    python3 translate.py --keys-file work/pilot_keys.json --out work/translations.jsonl
    python3 translate.py --all --out work/translations.jsonl          # every non-excluded item
    python3 translate.py --keys 3109 3538 --out work/translations.jsonl --retry-note "..."   # re-translation

One row per item: source key, the model's JSON output, usage, provider and the
settings used. Re-running skips keys already translated without error, unless
--force is given (re-translations append a new row; the newest row per key wins).
The guideline file is the system prompt, verbatim, so any change to it is visible in git.
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "ifeval_input_data.jsonl"
SOURCE_SHA256 = "6a85310ca8ce15eff755aa08a3a4ff931c7e273e7515ebb3c492ea85fd8288f2"  # google/IFEval@966cd89 ifeval_input_data.jsonl
MODEL = "google/gemini-3.1-pro-preview"
PROVIDER = "google-vertex/global/flex"
REASONING = {"effort": "high"}
EXCLUDE_PREFIXES = ("change_case:",)
EXCLUDE_IDS = {"keywords:letter_frequency"}


def excluded(row) -> bool:
    return any(i.startswith(EXCLUDE_PREFIXES) or i in EXCLUDE_IDS for i in row["instruction_id_list"])


def item_json(row) -> str:
    kwargs = [{k: v for k, v in (d or {}).items() if v is not None} for d in row["kwargs"]]
    return json.dumps({"prompt": row["prompt"], "instruction_id_list": row["instruction_id_list"],
                       "kwargs": kwargs}, ensure_ascii=False)


async def translate_one(session, key, system, row, note, sem):
    user = item_json(row)
    if note:
        user += "\n\nREVIEW NOTE ON A PREVIOUS TRANSLATION OF THIS ITEM (fix it): " + note
    body = {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": 32000, "reasoning": REASONING, "usage": {"include": True},
            "response_format": {"type": "json_object"},
            "provider": {"only": [PROVIDER], "allow_fallbacks": False}}
    err = None
    async with sem:
        for attempt in range(6):
            try:
                async with session.post("https://openrouter.ai/api/v1/chat/completions", json=body,
                                        headers={"Authorization": f"Bearer {key}"},
                                        timeout=aiohttp.ClientTimeout(total=1800)) as r:
                    d = await r.json()
                if "error" in d:
                    raise RuntimeError(json.dumps(d["error"])[:300])
                c = d["choices"][0]
                text = c["message"].get("content") or ""
                m = re.search(r"\{.*\}", text, re.S)
                out = json.loads(m.group(0))
                u = d.get("usage") or {}
                return {"key": row["key"], "output": out, "finish_reason": c.get("finish_reason"),
                        "provider": d.get("provider"), "completion_tokens": u.get("completion_tokens"),
                        "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                        "cost": u.get("cost"), "retry_note": note or None, "error": None}
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
                await asyncio.sleep(min(5 * 2 ** attempt, 60))
    return {"key": row["key"], "output": None, "retry_note": note or None, "error": err}


async def main_async(args):
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY is not set")
    system = (HERE / "translation_guideline.md").read_text()
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        sys.exit(f"{SOURCE}: SHA-256 mismatch; run ./download_source.sh")
    rows = {r["key"]: r for r in map(json.loads, SOURCE.open())}
    if args.all:
        keys = [k for k, r in rows.items() if not excluded(r)]
    elif args.keys_file:
        keys = json.loads(Path(args.keys_file).read_text())
    else:
        keys = args.keys
    out = Path(args.out)
    done = set()
    if out.exists() and not args.force:
        done = {r["key"] for r in map(json.loads, out.open()) if not r["error"]}
    todo = [k for k in keys if k not in done and not excluded(rows[k])]
    print(f"{len(todo)} to translate ({len(keys) - len(todo)} skipped)")
    meta = {"model": MODEL, "provider_pin": PROVIDER, "reasoning": REASONING, "temperature": 0,
            "guideline_sha256": hashlib.sha256(system.encode()).hexdigest(),
            "utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    sem = asyncio.Semaphore(args.concurrency)
    async with aiohttp.ClientSession() as s:
        with out.open("a", encoding="utf-8") as f:
            for coro in asyncio.as_completed([translate_one(s, key, system, rows[k], args.retry_note, sem) for k in todo]):
                r = await coro
                f.write(json.dumps({**r, **meta}, ensure_ascii=False) + "\n")
                f.flush()
                print(f"  {r['key']}: {'ok' if not r['error'] else 'ERROR ' + r['error'][:80]}  ${r.get('cost') or 0:.4f}")


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--keys-file")
    g.add_argument("--keys", nargs="+", type=int)
    p.add_argument("--out", required=True)
    p.add_argument("--retry-note", default="")
    p.add_argument("--force", action="store_true")
    p.add_argument("--concurrency", type=int, default=8)
    asyncio.run(main_async(p.parse_args()))


if __name__ == "__main__":
    main()
