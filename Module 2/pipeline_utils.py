import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RAW_DIR = RESULTS_DIR / "raw"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_prompt() -> str:
    return (BASE_DIR / "mars_deployment_prompt.txt").read_text(encoding="utf-8")


def default_parser(script_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Run {script_name}")
    parser.add_argument("--model", required=True, help="OpenRouter model id")
    parser.add_argument(
        "--output",
        default=str(RAW_DIR / f"{script_name}.json"),
        help="Output JSON path",
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=1600)
    return parser


def write_json(path: str, payload: Dict[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

