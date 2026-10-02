"""One OpenRouter chat call with retries that never turn infrastructure into a model answer.

Retried (never an outcome): HTTP 429/5xx, transport errors and timeouts, an
`error` object in a 200 body, and an empty `content` with finish_reason "stop"
(a serving-side failure in which the decision stays in the reasoning and is never
emitted as content). Not retried: finish_reason "length" -- a
truncation is the model's outcome, and retrying it would give that model pass@k.
"""

import asyncio
import json

import aiohttp

from common.models import OPENROUTER_URL, REASONING_MANDATORY


class CallFailed(RuntimeError):
    """Retries exhausted; the caller logs the row as an error and retries it on the next run."""


async def chat(session: aiohttp.ClientSession, api_key: str, model_id: str, provider: str,
               messages: list[dict], *, reasoning: bool, max_tokens: int, retries: int = 8,
               timeout_s: int = 3600) -> dict:
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "reasoning": {"enabled": reasoning or model_id in REASONING_MANDATORY},
        "usage": {"include": True},
        "provider": {"only": [provider], "allow_fallbacks": False},
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last = None
    for attempt in range(retries):
        backoff = min(3 * 2**attempt, 60)
        try:
            async with session.post(OPENROUTER_URL, headers=headers, json=payload,
                                    timeout=aiohttp.ClientTimeout(total=timeout_s)) as r:
                body = await r.text()
                if r.status == 429 or r.status >= 500:
                    last = f"HTTP {r.status}: {body[:300]}"
                    # Upstream rate limits (seen on Crusoe for Gemma 4 31B) clear on a minute scale.
                    wait = float(r.headers.get("Retry-After") or (max(backoff, 30) if r.status == 429 else backoff))
                    await asyncio.sleep(wait)
                    continue
                if r.status != 200:
                    raise CallFailed(f"HTTP {r.status}: {body[:300]}")
                data = json.loads(body)
                if "error" in data:
                    last = f"API error: {json.dumps(data['error'])[:300]}"
                    await asyncio.sleep(backoff)
                    continue
                choice = data["choices"][0]
                content = choice["message"].get("content") or ""
                if choice.get("finish_reason") == "stop" and not content.strip():
                    last = "empty content with finish_reason stop"
                    await asyncio.sleep(backoff)
                    continue
                usage = data.get("usage") or {}
                reasoning_text = choice["message"].get("reasoning") or ""
                return {
                    "response": content,
                    "finish_reason": choice.get("finish_reason"),
                    "provider": data.get("provider"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                    "cost": usage.get("cost"),
                    # Kept only for truncated replies, to tell a degenerate loop from a
                    # long but converging trace. Providers that return no reasoning text
                    # (e.g. OpenAI) leave it empty.
                    "reasoning_chars": len(reasoning_text),
                    "reasoning_tail": reasoning_text[-3000:] if choice.get("finish_reason") == "length" else None,
                }
        except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError, KeyError) as e:
            last = f"{type(e).__name__}: {e}"
            await asyncio.sleep(backoff)
    raise CallFailed(last or "retries exhausted")
