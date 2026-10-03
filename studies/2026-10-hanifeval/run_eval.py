#!/usr/bin/env python3
"""Evaluate OpenRouter models on HanIFEval v1 and log one scored row per item.

Usage (from this directory, after `set -a; source ../../.env`):
    python3 run_eval.py --models gpt-6-luna --subset pilot --out eval/pilot
    python3 run_eval.py --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 \
        --subset all --confirm-full --out eval/main

Items come from release/hanifeval_v1.jsonl (--release 1) or hanifeval_v1.1.jsonl (--release 1.1). The prompt is sent as the single user message, as in
IFEval. Settings follow studies/2026-10-korean (same models, pinned providers, reasoning on at the
provider default, temperature 0, max_tokens 64000, one sample per item).

Rows go to <out>/<model>.jsonl. Re-running resumes: rows with an `error` (API/transport failure,
budget stop) are dropped and retried, scored rows are kept. Settings are pinned in
<out>/<model>.config.json, and a resume with different settings or a changed item is refused.

Scoring is the vendored checker (checker/utils.py), strict and loose, per instruction and per prompt.
A response cut at max_tokens (finish_reason "length") is still scored as IFEval scores any text, and
is flagged `truncated` so the analysis can report it separately; infrastructure failures are never
scored.
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import aiohttp

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1])]
from checker.utils import InputExample, test_instruction_following_loose, test_instruction_following_strict  # noqa: E402
from common.models import ALL_MODELS, MODEL_CONCURRENCY_CAP  # noqa: E402
from common.openrouter import CallFailed, chat  # noqa: E402

RELEASES = {"1": HERE / "release" / "hanifeval_v1.jsonl", "1.1": HERE / "release" / "hanifeval_v1.1.jsonl"}
PILOT_KEYS = HERE / "work" / "pilot_keys.json"   # the 28-item translation pilot: covers all 21 instruction types


def item_sha(it):
    return hashlib.sha256(json.dumps([it["prompt"], it["instruction_id_list"], it["kwargs"]],
                                     ensure_ascii=False).encode()).hexdigest()


def score(it, response):
    inp = InputExample(key=it["key"], instruction_id_list=it["instruction_id_list"], prompt=it["prompt"],
                       kwargs=it["kwargs"])
    s = test_instruction_following_strict(inp, response)
    lo = test_instruction_following_loose(inp, response)
    return {"strict": s.follow_all_instructions, "loose": lo.follow_all_instructions,
            "strict_list": s.follow_instruction_list, "loose_list": lo.follow_instruction_list}


async def remaining_credit(session, key):
    """Smaller of the account balance (/credits) and this key's limit (/key limit_remaining)."""
    h = {"Authorization": f"Bearer {key}"}
    async with session.get("https://openrouter.ai/api/v1/credits", headers=h) as r:
        c = (await r.json())["data"]
    vals = [c["total_credits"] - c["total_usage"]]
    async with session.get("https://openrouter.ai/api/v1/key", headers=h) as r:
        lim = (await r.json())["data"].get("limit_remaining")
    if lim is not None:
        vals.append(lim)
    return min(vals)


async def credit_watch(session, key, floor, state):
    while True:
        try:
            rem = await remaining_credit(session, key)
            state["remaining"] = rem
            if rem < floor:
                state["stop"] = f"spendable credit ${rem:.2f} below --min-credit ${floor:.2f}"
                print(f"BUDGET STOP: {state['stop']}", flush=True)
                return
        except (aiohttp.ClientError, KeyError, TypeError, ValueError):
            pass
        await asyncio.sleep(60)


def load_done(path, items):
    if not path.exists():
        return set()
    rows = [json.loads(l) for l in path.open(encoding="utf-8")]
    kept = [r for r in rows if not r["error"]]
    for r in kept:
        if item_sha(items[r["key"]]) != r["item_sha256"]:
            sys.exit(f"{path}: item {r['key']} was logged with different item text; use a new --out.")
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept))
    return {r["key"] for r in kept}


async def main_async(args):
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY is not set")
    RELEASE = RELEASES[args.release]
    items = {r["key"]: r for r in map(json.loads, RELEASE.open())}
    if args.keys:
        keys = args.keys
    elif args.subset == "pilot":
        keys = json.loads(PILOT_KEYS.read_text())
        keys = keys["keys"] if isinstance(keys, dict) else keys
    else:
        keys = sorted(items)
    out = HERE / args.out
    out.mkdir(parents=True, exist_ok=True)
    release_sha = hashlib.sha256(RELEASE.read_bytes()).hexdigest()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=args.concurrency)) as session:
        budget = {"stop": None}
        watcher = asyncio.create_task(credit_watch(session, key, args.min_credit, budget))
        for name in args.models:
            model_id, provider, _, _ = ALL_MODELS[name]
            cfg = {"model_id": model_id, "provider": provider, "reasoning": args.reasoning == "on",
                   "max_tokens": args.max_tokens, "temperature": 0, "release_sha256": release_sha}
            cfg_path = out / f"{name}.config.json"
            if cfg_path.exists():
                prev = json.loads(cfg_path.read_text())
                clash = [k for k in cfg if prev.get(k) != cfg[k]]
                if clash:
                    sys.exit(f"{cfg_path}: logged under different settings ({', '.join(clash)}); use a new --out.")
            cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
            path = out / f"{name}.jsonl"
            done = load_done(path, items)
            todo = [k for k in keys if k not in done]
            print(f"{name}: {len(todo)} to run ({len(done)} logged)", flush=True)
            sem = asyncio.Semaphore(min(args.concurrency, MODEL_CONCURRENCY_CAP.get(name, args.concurrency)))

            async def one(k, model_id=model_id, provider=provider):
                it = items[k]
                row = {"key": k, "item_sha256": item_sha(it), "subset": it["subset"],
                       "instruction_id_list": it["instruction_id_list"], "error": None}
                async with sem:
                    if budget["stop"]:
                        return {**row, "error": f"budget stop: {budget['stop']}"}
                    try:
                        res = await chat(session, key, model_id, provider,
                                         [{"role": "user", "content": it["prompt"]}],
                                         reasoning=args.reasoning == "on", max_tokens=args.max_tokens)
                    except CallFailed as e:
                        return {**row, "error": f"model call: {e}"}
                row.update(res)
                row["truncated"] = res["finish_reason"] == "length"
                row.update(score(it, res["response"]))
                return row

            start = time.time()
            with path.open("a", encoding="utf-8") as log:
                for coro in asyncio.as_completed([one(k) for k in todo]):
                    r = await coro
                    log.write(json.dumps(r, ensure_ascii=False) + "\n")
                    log.flush()
                    tag = "ERROR " + r["error"][:70] if r["error"] else (
                        f"strict={int(r['strict'])} loose={int(r['loose'])}"
                        f"{' TRUNC' if r['truncated'] else ''} ${r.get('cost') or 0:.4f}")
                    print(f"  {name} {r['key']:5d} {tag}", flush=True)
            print(f"{name}: done in {time.time() - start:.0f}s", flush=True)
        watcher.cancel()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", required=True, choices=list(ALL_MODELS))
    p.add_argument("--subset", choices=["pilot", "all"], default="pilot")
    p.add_argument("--keys", nargs="+", type=int, default=None, help="run exactly these keys (diagnostics)")
    p.add_argument("--confirm-full", action="store_true", help="required with --subset all")
    p.add_argument("--reasoning", choices=["on", "off"], default="on")
    p.add_argument("--max-tokens", type=int, default=64000)
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--out", required=True)
    p.add_argument("--min-credit", type=float, default=2.0)
    p.add_argument("--release", choices=list(RELEASES), default="1",
                   help="dataset version; the release SHA-256 is pinned in each model's config")
    args = p.parse_args()
    if args.subset == "all" and not args.confirm_full and not args.keys:
        sys.exit("--subset all runs 429 items per model; add --confirm-full.")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
