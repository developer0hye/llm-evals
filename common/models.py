"""Models under test, their pinned OpenRouter providers, and the smoke-test model.

Every model is pinned to one provider (`provider.only`, `allow_fallbacks: false`):
unpinned, OpenRouter load-balances each call across providers with different
hardware, quantization and serving stacks. Prices are the pinned endpoint's list
price from OpenRouter's /models/<id>/endpoints on 2026-09-29 (solar-mini4: 2026-10-03),
in $ per 1M tokens.
"""

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# short name -> (OpenRouter model id, provider tag, $ in, $ out)
MODELS = {
    "deepseek-v4.1-flash": ("deepseek/deepseek-v4.1-flash", "streamlake/fp8", 0.15, 0.60),
    "gpt-6-luna": ("openai/gpt-6-luna", "openai", 0.10, 0.50),
    "glm-5.3-flash": ("z-ai/glm-5.3-flash", "z-ai/fp8", 0.15, 0.50),
    "solar-pro4": ("upstage/solar-pro4", "upstage", 0.09, 0.36),
    "solar-mini4": ("upstage/solar-mini4", "upstage", 0.05, 0.20),
    # Gemma 4 26B and 31B were dropped from studies/2026-10-korean on 2026-09-30:
    # 31B's only healthy bf16 pin (Crusoe) rate-limits upstream, and 26B does not
    # terminate with reasoning on. Kept here for their pilot rows; see that study's README.
    # CoreWeave bf16 was the first pin; it rejected even 4 concurrent 2k-token calls with
    # upstream 429 on 2026-09-29, so the pilot moved to NextBit bf16 before any main run.
    "gemma-4-26b": ("google/gemma-4-26b-a4b-it", "nextbit/bf16", 0.09, 0.30),
    "gemma-4-31b": ("google/gemma-4-31b-it", "crusoe/bf16", 0.14, 0.40),
}

# Cheapest pin that returned provider and usage.cost on a reasoning probe
# (2026-09-29): OpenAI's flex tier of GPT-6 Luna. Used for smoke runs on the
# golden samples only; never for reported results.
SMOKE_MODELS = {
    "gpt-6-luna-flex": ("openai/gpt-6-luna", "openai/flex", 0.05, 0.25),
}

ALL_MODELS = {**MODELS, **SMOKE_MODELS}

# Per-model cap on requests in flight, below run.py's --concurrency (see the
# provider-limits table in the root README). Crusoe returned "temporarily
# rate-limited upstream" (HTTP 429) for Gemma 4 31B at 8 in flight on
# 2026-09-29; NextBit served Gemma 4 26B at 4 in flight in a probe.
MODEL_CONCURRENCY_CAP = {"gemma-4-31b": 4, "gemma-4-26b": 4}

# Endpoints that reject `reasoning: {enabled: false}`.
REASONING_MANDATORY = {"z-ai/glm-5.3-flash"}
