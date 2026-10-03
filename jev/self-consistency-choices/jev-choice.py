import json
from utils import RUBRIC_HASH

BASE_MODELS = [
    "claude-haiku-4-5",
    "gpt-5.4-mini",
]

REASONING_MODELS = [
    "gpt-5.5",
    "claude-opus-4-8",
]

NUM_SAMPLES = 15

CONDITIONS = []
for (
    model
) in BASE_MODELS:  # non-reasoning models: dist at t=0 / default, then a single-pick variant
    for temp_value, temp_label in ((0, "0"), (None, "default")):
        CONDITIONS.append(
            {
                "label": f"{model} t={temp_label}",
                "model": model,
                "temp": temp_value,
                "mode": "dist",
            }
        )
    CONDITIONS.append(
        {
            "label": f"{model} single-pick t=0",
            "model": model,
            "temp": 0,
            "mode": "single",
        }
    )
CONDITIONS += [  # reasoning models: one distribution condition each
    {
        "label": f"{model}-reasoning",
        "model": model,
        "temp": None,
        "mode": "dist",
    }
    for model in REASONING_MODELS
]
# print(json.dumps(CONDITIONS, ensure_ascii=False, indent=2))
LABELS = [condition["label"] for condition in CONDITIONS]
TYPESAFE_LABEL = "typesafe_choice"
ALL_LABELS = [*LABELS, TYPESAFE_LABEL]

print(ALL_LABELS)

runs: dict[
    str, list
] = {}  # label -> NUM_SAMPLES samples of {question key: distribution}
stats: dict[str, list] = {}  # label -> NUM_SAMPLES (cost_usd, latency_s) pairs
with ThreadPoolExecutor(max_workers=16) as pool:
    futures = {
        condition["label"]: [
            pool.submit(
                ask_llm_rubric,
                condition["model"],
                condition["mode"],
                condition["temp"],
                sample_index,
                RUBRIC_HASH,
            )
            for sample_index in range(NUM_SAMPLES)
        ]
        for condition in CONDITIONS
    }
    for label, sample_futures in futures.items():
        results = [future.result() for future in sample_futures]
        runs[label] = [result[0] for result in results]
        stats[label] = [(result[1], result[2]) for result in results]

# # TypeSafe samples are drawn sequentially, after the LLM pool has closed, so each call's latency is a
# # clean round trip rather than one measured under the 16-way LLM thread contention.
# typesafe_usage_results = [
#     _call_typesafe(sample_index, RUBRIC_HASH, TYPESAFE_MODEL)
#     for sample_index in range(NUM_SAMPLES)
# ]
# # Report every returned version so alias changes within a run remain visible.
# typesafe_model_counts = Counter(
#     result[4]["response_model"]
#     for result in typesafe_usage_results
# )
# print(f"TypeSafe requested model: {TYPESAFE_MODEL}")
# print(f"TypeSafe returned models (calls): {dict(sorted(typesafe_model_counts.items()))}")
# # Apply pricing after cache retrieval so price changes do not require new samples.
# typesafe_results = [
#     (distributions, _cost(TYPESAFE_PRICE, input_tokens, output_tokens), latency)
#     for distributions, input_tokens, output_tokens, latency, _metadata in typesafe_usage_results
# ]
# typesafe_runs = [result[0] for result in typesafe_results]
# stats[TYPESAFE_LABEL] = [(result[1], result[2]) for result in typesafe_results]