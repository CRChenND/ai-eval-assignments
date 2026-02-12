#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Defaults (can be overridden by env vars before running this script)
ZERO_MODEL="${ZERO_MODEL:-qwen/qwen3-32b}"
COT_MODEL="${COT_MODEL:-qwen/qwen3-32b}"
ITER_MODEL="${ITER_MODEL:-qwen/qwen3-32b}"
REASON_MODEL="${REASON_MODEL:-qwen/qwq-32b}"
TOOL_MODEL="${TOOL_MODEL:-qwen/qwen3-32b}"
ITER_RUNS="${ITER_RUNS:-5}"
SKIP_SYNC="${SKIP_SYNC:-0}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "ERROR: OPENROUTER_API_KEY is not set."
  echo "Set it in ${ROOT_DIR}/.env or export it in your shell."
  exit 1
fi

cd "${SCRIPT_DIR}"

if [[ "${SKIP_SYNC}" != "1" ]]; then
  echo "[1/9] uv sync"
  uv sync
else
  echo "[1/9] skip uv sync (SKIP_SYNC=1)"
fi

echo "[2/9] generate_zero_shot.py"
uv run python generate_zero_shot.py --model "${ZERO_MODEL}"

echo "[3/9] generate_cot.py"
uv run python generate_cot.py --model "${COT_MODEL}"

echo "[4/9] generate_iterative.py"
uv run python generate_iterative.py --model "${ITER_MODEL}" --runs "${ITER_RUNS}"

echo "[5/9] generate_reasoning_model.py"
uv run python generate_reasoning_model.py --model "${REASON_MODEL}"

echo "[6/9] generate_tool_augmented.py"
uv run python generate_tool_augmented.py --model "${TOOL_MODEL}"

echo "[7/9] extract_claims.py + fact_check.py"
uv run python extract_claims.py
uv run python fact_check.py

echo "[8/9] analyze_results.py"
uv run python analyze_results.py

echo "[9/9] plot_results.py"
uv run python plot_results.py

echo "Done. Outputs:"
echo "  ${SCRIPT_DIR}/results/raw/"
echo "  ${SCRIPT_DIR}/results/claims/claims.json"
echo "  ${SCRIPT_DIR}/results/fact_check/fact_check.json"
echo "  ${SCRIPT_DIR}/results/analysis/metrics.json"
echo "  ${SCRIPT_DIR}/results/plots/"
