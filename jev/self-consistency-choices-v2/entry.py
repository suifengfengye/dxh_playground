from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import os
from time import perf_counter
from secrets import token_hex
import json
import numpy as np

from data import QUESTIONS, POST

CONDITIONS = [
  {
    "label": "qwen/qwen3.8-flash t=0",
    "model": "qwen/qwen3.8-flash",
    "temp": 0,
    "mode": "dist"
  },
  {
    "label": "qwen/qwen3.8-max-0902 t=0",
    "model": "qwen/qwen3.8-max-0902",
    "temp": 0,
    "mode": "dist"
  },
]

# NUM_SAMPLES = 15
NUM_SAMPLES = 1

LLM_PRICES = {  # $ per 1M tokens (input, output); prices + model ids as of 2026-07, see README
    "qwen/qwen3.8-flash": (0.15, 0.47),
    "qwen/qwen3.8-max-0902": (2, 6),
}

# print(f"OPENROUTER_API_KEY: {os.environ['OPENROUTER_API_KEY']}")
openai_client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

def _cost(prices: tuple[float, float], input_tokens: int, output_tokens: int) -> float:
    return input_tokens / 1e6 * prices[0] + output_tokens / 1e6 * prices[1]

def rubric_prompt(mode: str, sample_index: int, rubric_hash: str) -> str:
    """The post + all questions (with their label sets) in one prompt; ``mode`` picks the format.

    ``mode="dist"`` asks for a probability distribution over each question's labels; the single-pick
    mode (``mode="single"``) asks for a single label per question. The uid line combines
    ``rubric_hash`` (which rubric version) with ``sample_index`` and a random token, so every repeat
    is a distinct, independent draw and two different rubrics never share a nonce."""
    lines = []
    for key, (instructions, choices) in QUESTIONS.items():
        labels = "\n".join(f"     {label}: {desc}" for label, desc in choices.items())
        lines.append(f"- {key}: {instructions}\n   labels:\n{labels}")
    exclusivity = (
        "\n\n每个问题的标签都是互斥的：有且仅有一个适用。如果一篇帖子可能勉强符合多个标签，请根据标签描述选择最严重/最具体的那一个。"
    )
    if mode == "single":
        answer_format = (
            "\n\n对于每个问题，请恰好选择一个标签。\n请仅以 JSON 对象的形式作答，将每个问题的键（key）映射到该问题对应的纯标签文本（仅标签本身，不含描述），每个问题对应一个条目。"
        )
    else:
        answer_format = (
            "\n\n对于每个问题，请给出该问题所有标签的概率分布（取值范围 0.00–1.00，且总和为 1）。\n请仅以 JSON 对象的形式作答，将每个问题的键（key）映射到一个对象，该对象将该问题的纯标签文本（仅标签本身，不含描述）映射到对应的概率值，每个问题对应一个条目。"
        )
    return (
        f"uid: {rubric_hash}:{sample_index}:{token_hex(4)}\n\n"
        f"Document (a reported user post):\n{json.dumps(POST, indent=2)}\n\nQuestions:\n"
        + "\n".join(lines)
        + exclusivity
        + answer_format
    )

def _call_llm(model: str, prompt: str, temperature: float | None):
    """One LLM call -> (text, cost_usd, latency_s), routed by model name."""
    started = perf_counter()
    kwargs = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    if temperature is not None:
        kwargs["temperature"] = temperature
    # print(f"kwargs: {kwargs}")
    response = openai_client.chat.completions.create(**kwargs)
    print(f"response: {response}")
    text = response.choices[0].message.content
    usage = (response.usage.prompt_tokens, response.usage.completion_tokens)
    
    return text, _cost(LLM_PRICES[model], *usage), perf_counter() - started

def _numeric_value(value: object) -> float | None:
    """A finite numeric value, or ``None`` if the model emitted something unusable."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if np.isfinite(numeric) else None

def parse_distribution(raw: object, labels: list[str]) -> list[float]:
    """Map a model's already-parsed per-question reply to per-label probabilities, in label order
    (distribution-mode answers left un-normalized).

    A single-pick reply is a single label string -> all the mass on that exact label; a
    distribution-mode reply is a dict read label by label. Anything that doesn't match a known label
    or isn't a finite number is left NaN -- we report the gap rather than massaging the reply (e.g.
    stripping an echoed description) to make it fit."""
    if isinstance(raw, str):  # single-pick mode: a single chosen label
        if raw in labels:
            return [1.0 if label == raw else 0.0 for label in labels]
        return [float("nan")] * len(labels)
    if not isinstance(raw, dict):
        return [float("nan")] * len(labels)
    return [
        value if (value := _numeric_value(raw.get(label))) is not None else float("nan")
        for label in labels
    ]

def ask_llm_rubric(
    model: str,
    mode: str,
    temperature: float | None,
    sample_index: int,
    rubric_hash: str,
):
    """One LLM rubric query -> (per-question label distributions keyed by question key, cost_usd,
    latency_s); NaNs if the reply doesn't parse.

    ``mode="dist"`` parses 8 label distributions; the single-pick mode (``mode="single"``) parses 8
    single labels and puts all the mass on each. ``rubric_hash`` goes into the prompt's uid nonce
    (and so the cache key), so an edited state/rubric busts the cache instead of serving a stale
    answer."""
    prompt = rubric_prompt(mode, sample_index, rubric_hash)
    # print('*' * 100)
    # print('prompt:',prompt)
    text, cost, latency = _call_llm(model, prompt, temperature)
    # Peel a single ```json ... ``` fence (claude-haiku-4-5 sometimes adds one despite "ONLY a JSON
    # object").
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped[stripped.find("\n") + 1 :] if "\n" in stripped else ""
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[: -len("```")]
    try:
        raw = json.loads(stripped)
    except (ValueError, json.JSONDecodeError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    distributions = {
        key: parse_distribution(raw.get(key), list(choices))
        for key, (_instructions, choices) in QUESTIONS.items()
    }
    return distributions, cost, latency


with ThreadPoolExecutor(max_workers=16) as pool:
     fetures = {
        condition["label"]: [ pool.submit(ask_llm_rubric, condition["model"], condition["mode"], condition["temp"], sample_index, "rubric_hash_123456") for sample_index in range(NUM_SAMPLES)] for condition in CONDITIONS
     }
     for label, futures in fetures.items():
         for future in futures:
             print(label, future.result())