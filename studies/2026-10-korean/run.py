#!/usr/bin/env python3
"""Run the Korean study's four tasks on OpenRouter models and log one row per item.

Usage (from this directory, after ./download_data.sh and `set -a; source ../../.env`):
    python3 run.py --models gpt-6-luna-flex --judge gpt-6-luna-flex --out smoke          # golden samples
    python3 run.py --models gemma-4-26b --subset pilot --out pilot                          # per-model pilot
    python3 run.py --models gemma-4-26b --subset main --confirm-full --out results         # main run

Rows go to <out>/<model>/<task>.jsonl, keyed by item id. Re-running resumes:
logged items are skipped, rows with an `error` (API/transport failure, judge
failure) are dropped and retried. A resume refuses to mix settings: the model,
provider pin, reasoning flag, max_tokens and judge are pinned in
<out>/<model>/run_config.json, and every logged row's prompt and gold hashes
must match the current data. Question text is not logged separately, but the
`response` field can quote it (NER and LBox replies restate the input).
"""

import argparse
import asyncio
import importlib
import json
import os
import sys
import time
from pathlib import Path

import aiohttp

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1])]
from common.models import ALL_MODELS, MODEL_CONCURRENCY_CAP  # noqa: E402
from common.openrouter import CallFailed, chat  # noqa: E402
from tasks.base import TRUNCATED  # noqa: E402

TASKS = ["kobalt", "kosimpleqa", "klue_ner", "lbox_casename"]
MODULES = {"kobalt": "tasks.kobalt", "kosimpleqa": "tasks.kosimpleqa",
           "klue_ner": "tasks.klue_ner", "lbox_casename": "tasks.lbox_casename"}
LOGGED_META = {"kobalt": ["class", "level"], "kosimpleqa": ["category", "answer_type"],
               "klue_ner": ["source"], "lbox_casename": ["casetype", "label_leak"]}


def select(items, task, subset, ids_file=None):
    if ids_file:  # diagnostics: an explicit {task: [ids]} list, e.g. the truncated items of a pilot
        ids = set(json.loads(Path(ids_file).read_text()).get(task, []))
        return [i for i in items if i.id in ids]
    if subset == "all":
        return items
    ids = set(json.loads((HERE / "subsets.json").read_text())[subset][task])
    chosen = [i for i in items if i.id in ids]
    assert len(chosen) == len(ids), f"{task}: {subset} ids missing from data"
    return chosen


def guard(model_dir: Path, config: dict):
    path = model_dir / "run_config.json"
    if path.exists():
        prev = json.loads(path.read_text())
        clash = [k for k in config if prev.get(k) != config[k]]
        if clash:
            sys.exit(f"{path}: logged under different settings ({', '.join(clash)}); use a new --out.")
    model_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n")


def load_done(path: Path, items_by_id: dict) -> set:
    if not path.exists():
        return set()
    rows = [json.loads(l) for l in path.open(encoding="utf-8")]
    kept = [r for r in rows if not r["error"]]
    for r in kept:
        it = items_by_id.get(r["item"])
        if it and (it.prompt_sha256, it.gold_sha256) != (r["prompt_sha256"], r["gold_sha256"]):
            sys.exit(f"{path}: item {r['item']} was logged with a different prompt or gold; use a new --out.")
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept))
    return {r["item"] for r in kept}


class BudgetStop(Exception):
    pass


async def remaining_credit(session, key):
    """Spendable credit: the smaller of the account balance (/credits: total_credits - total_usage,
    shared with every key and project on the account) and this key's own limit (/key limit_remaining).
    /key alone is not the balance: it is a per-key cap, and was misread as the balance until 2026-10-01."""
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
    """Poll spendable credit every 60 s; below `floor`, stop starting new calls."""
    while True:
        try:
            remaining = await remaining_credit(session, key)
            if remaining < floor:
                state["stop"] = f"spendable credit ${remaining:.2f} below --min-credit ${floor:.2f}"
                print(f"BUDGET STOP: {state['stop']}", flush=True)
                return
        except (aiohttp.ClientError, KeyError, TypeError, ValueError):
            pass
        await asyncio.sleep(60)


async def main_async(args):
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY is not set")
    data_dir = HERE / "data"
    tasks = {t: importlib.import_module(MODULES[t]) for t in args.tasks}
    loaded = {t: select(m.load(data_dir), t, args.subset, args.ids) for t, m in tasks.items()}
    judge = ALL_MODELS[args.judge] if "kosimpleqa" in tasks else None
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=args.concurrency)) as session:
        budget = {"stop": None}
        watcher = asyncio.create_task(credit_watch(session, key, args.min_credit, budget))
        for name in args.models:
            model_id, provider, _, _ = ALL_MODELS[name]
            model_dir = HERE / args.out / name
            guard(model_dir, {"model_id": model_id, "provider": provider, "reasoning": args.reasoning == "on",
                              "max_tokens": args.max_tokens,
                              "judge": list(judge[:2]) if judge else None,
                              "subset": f"ids:{Path(args.ids).name}" if args.ids else args.subset})
            sem = asyncio.Semaphore(min(args.concurrency, MODEL_CONCURRENCY_CAP.get(name, args.concurrency)))
            for task, mod in tasks.items():
                items = loaded[task]
                path = model_dir / f"{task}.jsonl"
                done = load_done(path, {i.id: i for i in items})
                todo = [i for i in items if i.id not in done]
                print(f"{name} / {task}: {len(todo)} to run ({len(done)} logged)")

                async def one(item, mod=mod, task=task):
                    async with sem:
                        if budget["stop"]:  # logged as an error, so a later run with credit retries it
                            return {"task": task, "item": item.id, "prompt_sha256": item.prompt_sha256,
                                    "gold_sha256": item.gold_sha256, "error": f"budget stop: {budget['stop']}"}
                        row = {"task": task, "item": item.id, "prompt_sha256": item.prompt_sha256,
                               "gold_sha256": item.gold_sha256, "gold": item.gold,
                               **{k: item.meta[k] for k in LOGGED_META[task]}, "error": None}
                        try:
                            res = await chat(session, key, model_id, provider, item.messages,
                                             reasoning=args.reasoning == "on", max_tokens=args.max_tokens)
                        except CallFailed as e:
                            return {**row, "error": f"model call: {e}"}
                        row.update(res)
                        if res["finish_reason"] == "length":
                            pred, sc = None, {"outcome": TRUNCATED}
                            if task == "klue_ner":
                                sc.update(tp=0, fp=0, fn=len(item.gold))
                        else:
                            pred = mod.parse(item, res["response"])
                            sc = mod.score(item, pred)
                        row["pred"] = pred
                        row.update(sc)
                        if sc["outcome"] == "needs_judge":
                            for _ in range(3):
                                try:
                                    j = await chat(session, key, judge[0], judge[1], mod.judge_messages(item, pred),
                                                   reasoning=False, max_tokens=args.judge_max_tokens)
                                except CallFailed as e:
                                    return {**row, "error": f"judge call: {e}"}
                                grade = mod.parse_judge(j["response"])
                                if grade:
                                    break
                            row["judge"] = {"model_id": judge[0], "provider": j["provider"],
                                            "response": j["response"], "cost": j["cost"]}
                            if not grade:
                                return {**row, "error": f"judge reply not A/B/C: {j['response'][:80]!r}"}
                            row["outcome"] = grade
                        return row

                start = time.time()
                with path.open("a", encoding="utf-8") as log:
                    for coro in asyncio.as_completed([one(i) for i in todo]):
                        r = await coro
                        log.write(json.dumps(r, ensure_ascii=False) + "\n")
                        log.flush()
                        print(f"  {r['item'][:28]:28s} {r.get('outcome') or 'ERROR: ' + str(r['error'])[:60]}")
                print(f"  done in {time.time() - start:.0f}s")
        watcher.cancel()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", required=True, choices=list(ALL_MODELS))
    p.add_argument("--tasks", nargs="+", default=TASKS, choices=TASKS)
    p.add_argument("--subset", choices=["golden", "pilot", "main", "all"], default="golden",
                   help="item subsets from subsets.json (see make_subsets.py); all = every item")
    p.add_argument("--confirm-full", action="store_true", help="required with --subset main or all")
    p.add_argument("--ids", default=None, help="JSON {task: [ids]}: run exactly these items (diagnostics)")
    p.add_argument("--judge", default="gpt-6-luna-flex", choices=list(ALL_MODELS),
                   help="KoSimpleQA grader. The paper used GPT-4o; any choice is recorded per row")
    p.add_argument("--reasoning", choices=["on", "off"], default="on")
    p.add_argument("--max-tokens", type=int, default=64000,
                   help="Raised from 16000 on 2026-09-29, before any main run: in the 16k pilot, 5 of 5 "
                        "DeepSeek KoBALT items truncated at 16k finished on their own at 64k, 3 of them "
                        "in <=11.4k tokens (see README, Protocol)")
    p.add_argument("--judge-max-tokens", type=int, default=1024,
                   help="the grader answers with one letter; headroom is for judges that always reason")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--out", required=True)
    p.add_argument("--min-credit", type=float, default=2.0,
                   help="stop starting new calls when spendable credit (min of account balance and key limit) falls below this ($)")
    args = p.parse_args()
    if args.subset in ("main", "all") and not args.confirm_full:
        sys.exit(f"--subset {args.subset} runs the full evaluation (thousands of calls per model); "
                 "add --confirm-full to proceed.")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
