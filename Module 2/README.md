# Module 2 Pipeline (OpenRouter)

## 0) Setup

```bash
cd "/Users/chaoranchen/Documents/GitHub/ai-eval-assignments"
set -a
source .env
set +a

cd "Module 2"
uv sync
```

## 1) Run generation scripts

Replace model IDs with the OpenRouter models you want to test.

```bash
uv run python generate_zero_shot.py --model "qwen/qwen3-32b"
uv run python generate_cot.py --model "qwen/qwen3-32b"
uv run python generate_iterative.py --model "qwen/qwen3-32b" --runs 5
uv run python generate_reasoning_model.py --model "qwen/qwq-32b"
uv run python generate_tool_augmented.py --model "qwen/qwen3-32b"
```

## 2) Extract claims and fact-check

```bash
uv run python extract_claims.py
uv run python fact_check.py
uv run python analyze_results.py
```

## 3) Plot

```bash
uv run python plot_results.py
```

## One-command run

```bash
./run_all.sh
```

Optional overrides:

```bash
ITER_RUNS=3 REASON_MODEL="qwen/qwen3-32b" ./run_all.sh
SKIP_SYNC=1 ./run_all.sh
```

## Re-run specific strategies with higher token budget

```bash
set -a; source ../.env; set +a
uv run python generate_zero_shot.py --model "qwen/qwen3-32b" --max-tokens 4000
uv run python generate_cot.py --model "qwen/qwen3-32b" --max-tokens 4000
```

Then refresh metrics/plots:

```bash
uv run python extract_claims.py
uv run python fact_check.py
uv run python analyze_results.py
uv run python plot_results.py
```

## Update report after rerun

The report source is `main.tex`. Update strategy tables and conclusions using:

- `results/analysis/metrics.json`
- `results/fact_check/fact_check.json`
- `results/raw/*.json` (coverage / truncation status)
- `results/plots/*.png`

## Output structure

- `results/raw/*.json`: raw model outputs
- `results/claims/claims.json`: extracted claims
- `results/fact_check/fact_check.json`: claim-level fact-check results
- `results/analysis/metrics.json`: strategy-level metrics
- `results/plots/*.png`: figures for report
